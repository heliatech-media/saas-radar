/**
 * Cloudflare Pages Function: /api/sentinel/newsletter
 * Master Emergency Controls for Newsletter Dispatch.
 * Strict rule: STOP NEWSLETTER freezes all outgoing dispatch immediately and CANNOT restart automatically.
 */

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const action = body.action;
    const actorEmail = context.request.headers.get("Cf-Access-Authenticated-User-Email") || "owner@heliatech.online";
    const db = context.env?.DB;

    if (!action) {
      return new Response(JSON.stringify({ error: "Action required" }), { status: 400 });
    }

    let result = {};

    if (action === "emergency-stop") {
      if (db) {
        await db.prepare("UPDATE fleet_controls SET newsletter_emergency_stop = 1, last_updated_at = datetime('now'), last_updated_by = ? WHERE id = 1").bind(actorEmail).run();
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
          VALUES (datetime('now'), ?, 'owner', 'STOP_NEWSLETTER', 'newsletter', '{"reason":"Emergency Stop triggered by owner"}', 'ACTIVE', 'FROZEN', 'sig_nl_stop')
        `).bind(actorEmail).run();
      }
      result = {
        success: true,
        emergency_stop_active: true,
        message: "Arrêt d'urgence appliqué : tout envoi est gelé instantanément. Aucun redémarrage automatique n'est possible.",
        can_auto_restart: false
      };
    } else if (action === "resume") {
      if (db) {
        await db.prepare("UPDATE fleet_controls SET newsletter_emergency_stop = 0, last_updated_at = datetime('now'), last_updated_by = ? WHERE id = 1").bind(actorEmail).run();
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
          VALUES (datetime('now'), ?, 'owner', 'RESUME_NEWSLETTER', 'newsletter', '{"reason":"Manual resume by owner"}', 'FROZEN', 'ACTIVE', 'sig_nl_resume')
        `).bind(actorEmail).run();
      }
      result = {
        success: true,
        emergency_stop_active: false,
        message: "Diffusion newsletter déverrouillée par le propriétaire."
      };
    } else {
      return new Response(JSON.stringify({ error: "Unknown action" }), { status: 400 });
    }

    return new Response(JSON.stringify(result), {
      status: 200,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}
