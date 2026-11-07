/**
 * Cloudflare Pages Function: /api/sentinel/approvals
 * Human-in-the-Loop Sovereign Approval Queue.
 * Strictly queries Cloudflare D1 table owner_approvals.
 * ZÉRO MOCK, ZÉRO HARDCODED APPROVAL.
 */

export async function onRequestGet(context) {
  try {
    const db = context.env?.DB;

    if (!db) {
      return new Response(JSON.stringify({
        error: "Erreur technique : Base D1 non connectée sur ce runtime.",
        approvals: [],
        count: 0
      }), {
        status: 503,
        headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
      });
    }

    let items = [];
    const rows = await db.prepare("SELECT * FROM owner_approvals WHERE status = 'PENDING' ORDER BY id ASC").all();
    if (rows && rows.results) items = rows.results;

    return new Response(JSON.stringify({
      approvals: items,
      count: items.length,
      source: "Cloudflare D1 table owner_approvals"
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message, approvals: [], count: 0 }), { status: 500 });
  }
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const { approval_id, decision, decision_notes } = body;
    const actorEmail = context.request.headers.get("Cf-Access-Authenticated-User-Email") || "owner@heliatech.online";
    const db = context.env?.DB;

    if (!approval_id || !decision || !["APPROVED", "REJECTED"].includes(decision)) {
      return new Response(JSON.stringify({ error: "approval_id et décision valide ('APPROVED'|'REJECTED') requis" }), { status: 400 });
    }

    if (!db) {
      return new Response(JSON.stringify({ error: "Erreur technique : Base D1 non disponible pour enregistrer la décision." }), { status: 503 });
    }

    const item = await db.prepare("SELECT * FROM owner_approvals WHERE id = ?").bind(approval_id).first();
    if (!item) {
      return new Response(JSON.stringify({ error: `Élément introuvable en base D1 pour l'ID ${approval_id}.` }), { status: 404 });
    }

    // 1. Mettre à jour l'approbation en base D1
    await db.prepare(`
      UPDATE owner_approvals 
      SET status = ?, decided_at = datetime('now'), decided_by = ?, decision_notes = ?
      WHERE id = ?
    `).bind(decision, actorEmail, decision_notes || "", approval_id).run();

    // 2. Si c'est une édition newsletter, synchroniser son statut
    if (item.item_type === "newsletter_edition") {
      const newStatus = decision === "APPROVED" ? "validated" : "cancelled";
      await db.prepare("UPDATE newsletter_editions SET status = ?, validated_at = datetime('now') WHERE slot_key = ?")
        .bind(newStatus, item.item_ref).run();
    }

    // 3. Consigner formellement dans le journal d'audit immuable
    await db.prepare(`
      INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
      VALUES (datetime('now'), ?, 'owner', 'DECIDE_APPROVAL', ?, ?, 'PENDING', ?, 'sig_decision_hash')
    `).bind(actorEmail, `approval:${approval_id}`, JSON.stringify({ item_ref: item.item_ref, decision, notes: decision_notes }), decision).run();

    return new Response(JSON.stringify({
      success: true,
      approval_id,
      decision,
      message: decision === "APPROVED" ? "Élément validé avec succès en base D1 pour publication/diffusion." : "Élément rejeté et archivé en base D1."
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}
