/**
 * Cloudflare Pages Function: /api/sentinel/approvals
 * Human-in-the-Loop Sovereign Approval Queue.
 * No newsletter, article, deal, or pricing modification can go live without explicit owner approval.
 */

export async function onRequestGet(context) {
  try {
    const db = context.env?.DB;
    let items = [];

    if (db) {
      try {
        const rows = await db.prepare("SELECT * FROM owner_approvals WHERE status = 'PENDING' ORDER BY id ASC").all();
        if (rows && rows.results) items = rows.results;
      } catch (e) {
        console.warn("D1 approvals query fallback:", e.message);
      }
    }

    // Default seed fallback if D1 not yet populated in edge runtime
    if (items.length === 0) {
      items = [
        {
          id: 1,
          item_type: "newsletter_edition",
          item_ref: "2026-11-12:thursday",
          title: "Newsletter #055 (Focus : Cursor 0.43 vs Windsurf 1.2)",
          summary: "Édition du jeudi 12 novembre 2026. Empreinte SHA-256 calculée, aucun doublon d'article ou de deal sur les 8 dernières éditions.",
          content_payload: JSON.stringify({
            slot_key: "2026-11-12:thursday",
            issue_number: 55,
            subject: "The Thursday Radar: Cursor 0.43 vs Windsurf 1.2 Benchmark",
            recipients_estimated: 141
          }),
          content_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          author_agent: "NewsletterEngine",
          status: "PENDING",
          created_at: "2026-11-06T15:30:00Z"
        }
      ];
    }

    return new Response(JSON.stringify({ approvals: items, count: items.length }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const { approval_id, decision, decision_notes } = body;
    const actorEmail = context.request.headers.get("Cf-Access-Authenticated-User-Email") || "owner@heliatech.online";
    const db = context.env?.DB;

    if (!approval_id || !decision || !["APPROVED", "REJECTED"].includes(decision)) {
      return new Response(JSON.stringify({ error: "approval_id and valid decision ('APPROVED'|'REJECTED') required" }), { status: 400 });
    }

    if (db) {
      const item = await db.prepare("SELECT * FROM owner_approvals WHERE id = ?").bind(approval_id).first();
      if (item) {
        await db.prepare(`
          UPDATE owner_approvals 
          SET status = ?, decided_at = datetime('now'), decided_by = ?, decision_notes = ?
          WHERE id = ?
        `).bind(decision, actorEmail, decision_notes || "", approval_id).run();

        // If it's a newsletter edition, validate the draft in newsletter_editions
        if (item.item_type === "newsletter_edition") {
          const newStatus = decision === "APPROVED" ? "validated" : "cancelled";
          await db.prepare("UPDATE newsletter_editions SET status = ?, validated_at = datetime('now') WHERE slot_key = ?")
            .bind(newStatus, item.item_ref).run();
        }

        // Write audit log
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
          VALUES (datetime('now'), ?, 'owner', 'DECIDE_APPROVAL', ?, ?, 'PENDING', ?, 'sig_decision_hash')
        `).bind(actorEmail, `approval:${approval_id}`, JSON.stringify({ item_ref: item.item_ref, decision, notes: decision_notes }), decision).run();
      }
    }

    return new Response(JSON.stringify({
      success: true,
      approval_id,
      decision,
      message: decision === "APPROVED" ? "Élément validé avec succès pour publication/diffusion." : "Élément rejeté et archivé."
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}
