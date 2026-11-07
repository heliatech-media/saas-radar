/**
 * Cloudflare Pages Function: /api/sentinel/content
 * Dynamic Content Inventory & Evidence Ledger.
 * Strictly queries Cloudflare D1 table content_inventory.
 * ZÉRO SAMPLE DATA, ZÉRO HARDCODED ARTICLE.
 */

async function computeSha256(text) {
  const enc = new TextEncoder().encode(text);
  const hashBuf = await crypto.subtle.digest("SHA-256", enc);
  return Array.from(new Uint8Array(hashBuf))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

export async function onRequestGet(context) {
  try {
    const url = new URL(context.request.url);
    const limit = Math.min(parseInt(url.searchParams.get("limit") || "50", 10), 100);
    const db = context.env?.DB;

    if (!db) {
      return new Response(JSON.stringify({
        error: "Erreur technique : Base D1 non connectée sur ce runtime.",
        content: [],
        total: 0
      }), {
        status: 503,
        headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
      });
    }

    let items = [];
    let total = 0;

    const countRes = await db.prepare("SELECT COUNT(*) as c FROM content_inventory").first();
    if (countRes && countRes.c !== undefined) total = countRes.c;

    const rows = await db.prepare("SELECT * FROM content_inventory ORDER BY last_audited_at DESC LIMIT ?").bind(limit).all();
    if (rows && rows.results) items = rows.results;

    return new Response(JSON.stringify({
      content: items,
      total,
      source: "Cloudflare D1 table content_inventory"
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message, content: [], total: 0 }), { status: 500 });
  }
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const { action, slug } = body;
    const actorEmail = context.request.headers.get("Cf-Access-Authenticated-User-Email") || "owner@heliatech.online";
    const db = context.env?.DB;

    if (!slug) {
      return new Response(JSON.stringify({ error: "slug required" }), { status: 400 });
    }

    if (!db) {
      return new Response(JSON.stringify({ error: "Erreur technique : Base D1 non disponible pour enregistrer le réaudit." }), { status: 503 });
    }

    if (action === "re-audit") {
      const nowIso = new Date().toISOString();

      // Vérité Opérationnelle : Le clic patron demande un réaudit et passe au statut AUDIT_QUEUED
      await db.prepare("UPDATE content_inventory SET audit_status = 'AUDIT_QUEUED', last_audited_at = ? WHERE slug = ?")
        .bind(nowIso, slug).run();

            // Chaînage cryptographique SHA-256 avec le prev_hash du dernier log pour intégrité forensique
      let prevSig = "0".repeat(64);
      try {
        const lastLog = await db.prepare("SELECT signature FROM sentinel_audit_logs ORDER BY id DESC LIMIT 1").first();
        if (lastLog && lastLog.signature) {
          prevSig = lastLog.signature;
        }
      } catch (_) {}

      const targetRef = `content:${slug}`;
      const actionType = "REQUEST_CONTENT_REAUDIT";
      const detailsJson = JSON.stringify({ assigned_agent: "SoftwareAnalyst" });
      const sigPayload = `${prevSig}|${nowIso}|${actorEmail}|${actionType}|${targetRef}|AUDIT_QUEUED`;
      const signature = await computeSha256(sigPayload);

      await db.prepare(`
        INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
        VALUES (?, ?, 'owner', ?, ?, ?, 'VERIFIED', 'AUDIT_QUEUED', ?)
      `).bind(nowIso, actorEmail, actionType, targetRef, detailsJson, signature).run();

      return new Response(JSON.stringify({
        success: true,
        slug,
        audit_status: "AUDIT_QUEUED",
        last_audited_at: nowIso,
        message: `Ordre de réaudit enregistré : contenu '${slug}' placé en file d'attente ('AUDIT_QUEUED'). L'agent SoftwareAnalyst analysera et certifiera ce contenu au prochain cycle.`
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    }

    return new Response(JSON.stringify({ error: "Unknown action" }), { status: 400 });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}
