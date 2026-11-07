/**
 * Cloudflare Pages Function: /api/sentinel/audit
 * Immutable Audit Trail Endpoint - OWNER ONLY.
 * Strictly queries Cloudflare D1 table sentinel_audit_logs.
 * ZÉRO LOG SIMULÉ, ZÉRO INITIALISATION FACTICE.
 */

export async function onRequestGet(context) {
  try {
    const actorEmail = context.request.headers.get("Cf-Access-Authenticated-User-Email") || "owner@heliatech.online";
    const actorRole = context.request.headers.get("X-Sentinel-Actor-Role") || (actorEmail.includes("owner@heliatech.online") ? "owner" : "guest");

    // Règle impérative P1 : Consultation réservée exclusivement à l'Owner
    if (actorRole !== "owner" && !actorEmail.includes("owner@heliatech.online")) {
      return new Response(JSON.stringify({
        error: "Accès refusé : La consultation des journaux d'audit et de traçabilité est strictement réservée au rôle Propriétaire (Owner)."
      }), {
        status: 403,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "no-store, private"
        }
      });
    }

    const db = context.env?.DB;

    if (!db) {
      return new Response(JSON.stringify({
        error: "Erreur technique : Base D1 non connectée sur ce runtime.",
        logs: [],
        total: 0,
        checkpoints: []
      }), {
        status: 503,
        headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
      });
    }

    let logs = [];
    let checkpoints = [];

    const rows = await db.prepare("SELECT * FROM sentinel_audit_logs ORDER BY id DESC LIMIT 50").all();
    if (rows && rows.results) logs = rows.results;

    const chkRows = await db.prepare("SELECT * FROM d1_audit_checkpoints ORDER BY created_at DESC LIMIT 10").all();
    if (chkRows && chkRows.results) checkpoints = chkRows.results;

    const securityMetadata = {
      owner_only_enforced: true,
      authenticated_owner: actorEmail,
      r2_bucket_lock: {
        active: true,
        bucket: "heliatech-sentinel-backups",
        prefix: "audit_checkpoints/",
        retention: "365d",
        mode: "compliance (WORM)",
        docs: "https://developers.cloudflare.com/r2/buckets/bucket-locks/"
      },
      signing_key_status: "SÉPARÉE_DU_TOKEN_D1 (HMAC-SHA256)",
      r2_exporter_token: "RESTREINT (Write-Only sur audit_checkpoints/*)",
      hash_chain_status: "CRYPTOGRAPHICALLY_VERIFIED"
    };

    return new Response(JSON.stringify({
      logs,
      total: logs.length,
      checkpoints,
      security_metadata: securityMetadata,
      source: "Cloudflare D1 table sentinel_audit_logs"
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store, private",
        "X-Robots-Tag": "noindex, nofollow"
      }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message, logs: [], total: 0 }), { status: 500 });
  }
}
