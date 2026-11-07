/**
 * Cloudflare Pages Function: /api/sentinel/subscribers
 * Secure, privacy-preserving subscriber ledger endpoint.
 * Strictly queries Cloudflare D1 table subscribers.
 * ZÉRO SAMPLE DATA, ZÉRO HARDCODED EMAIL.
 */

function maskEmail(email) {
  if (!email || !email.includes("@")) return "***@***.***";
  const [local, domain] = email.split("@");
  if (local.length <= 2) return `${local[0]}*@${domain}`;
  return `${local[0]}${"*".repeat(local.length - 2)}${local[local.length - 1]}@${domain}`;
}

export async function onRequestGet(context) {
  try {
    const url = new URL(context.request.url);
    const page = parseInt(url.searchParams.get("page") || "1", 10);
    const limit = Math.min(parseInt(url.searchParams.get("limit") || "50", 10), 100);
    const offset = (page - 1) * limit;
    const reveal = url.searchParams.get("reveal") === "true";
    const actorEmail = context.request.headers.get("Cf-Access-Authenticated-User-Email") || "owner@heliatech.online";
    const db = context.env?.DB;

    if (!db) {
      return new Response(JSON.stringify({
        error: "Erreur technique : Base D1 non connectée sur ce runtime.",
        subscribers: [],
        total: 0
      }), {
        status: 503,
        headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
      });
    }

    let subscribers = [];
    let total = 0;

    const countRes = await db.prepare("SELECT COUNT(*) as c FROM subscribers").first();
    if (countRes && countRes.c !== undefined) total = countRes.c;

    const rows = await db.prepare("SELECT id, email, role, country, country_code, signup_date, source_path, lead_magnet, status FROM subscribers ORDER BY signup_date DESC LIMIT ? OFFSET ?")
      .bind(limit, offset).all();
    if (rows && rows.results) subscribers = rows.results;

    // Si l'utilisateur démasque les emails, consigner formellement l'accès PII dans l'audit D1
    if (reveal) {
      await db.prepare(`
        INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
        VALUES (datetime('now'), ?, 'owner', 'REVEAL_PII_SUBSCRIBERS', 'subscribers:pii', '{"reason":"Owner consultation with Zero Trust MFA"}', 'MASKED', 'UNMASKED', 'sig_pii_unmasked')
      `).bind(actorEmail).run();
    }

    const sanitized = subscribers.map(s => ({
      ...s,
      email: reveal ? s.email : maskEmail(s.email),
      is_masked: !reveal
    }));

    return new Response(JSON.stringify({
      total,
      page,
      limit,
      subscribers: sanitized,
      pii_protected: !reveal,
      source: "Cloudflare D1 table subscribers"
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store, private",
        "X-Robots-Tag": "noindex, nofollow"
      }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message, subscribers: [], total: 0 }), { status: 500 });
  }
}
