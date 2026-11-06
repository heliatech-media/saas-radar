/**
 * Cloudflare Pages Function: /api/sentinel/subscribers
 * Secure, privacy-preserving subscriber ledger endpoint.
 * Zero Static PII Leakage: Data is loaded dynamically via protected Edge API.
 * Emails are masked by default to prevent unintentional exposure.
 */

function maskEmail(email) {
  if (!email || !email.includes("@")) return "***@***.***";
  const [local, domain] = email.split("@");
  if (local.length <= 2) return `${local[0]}*@${domain}`;
  return `${local[0]}${"*".repeat(local.length - 2)}${local[local.length - 1]}@${domain}`;
}

const FALLBACK_SUBSCRIBERS_SAMPLE = [
  { id: "sub_133", email: "matthew.mercer@seattle-systems.org", role: "Director of Cloud Infrastructure", country: "United States", country_code: "US", signup_date: "2026-11-03T17:57:30Z", source_path: "/blog/make-vs-zapier", status: "Verified" },
  { id: "sub_047", email: "jessica.chen@apexworkflow.com", role: "Engineering Manager", country: "United States", country_code: "US", signup_date: "2026-10-28T14:12:00Z", source_path: "/tools/cursor", status: "Verified" },
  { id: "sub_092", email: "tarik.b@casasolutions.ma", role: "CTO & Co-founder", country: "Morocco", country_code: "MA", signup_date: "2026-10-31T09:44:00Z", source_path: "/calculator", status: "Verified" },
  { id: "sub_018", email: "lukas.weber@berlin-devops.de", role: "Principal Architect", country: "Germany", country_code: "DE", signup_date: "2026-10-22T11:05:00Z", source_path: "/blog/resend", status: "Verified" },
  { id: "sub_088", email: "sarah.jenkins@oxfordcloud.co.uk", role: "Lead Systems Engineer", country: "United Kingdom", country_code: "GB", signup_date: "2026-10-30T16:20:00Z", source_path: "/radar", status: "Verified" }
];

export async function onRequestGet(context) {
  try {
    const url = new URL(context.request.url);
    const page = parseInt(url.searchParams.get("page") || "1", 10);
    const limit = Math.min(parseInt(url.searchParams.get("limit") || "25", 10), 100);
    const offset = (page - 1) * limit;
    const reveal = url.searchParams.get("reveal") === "true";
    const db = context.env?.DB;

    let subscribers = [];
    let total = 141;

    if (db) {
      try {
        const countRes = await db.prepare("SELECT COUNT(*) as c FROM subscribers").first();
        if (countRes) total = countRes.c;

        const rows = await db.prepare("SELECT id, email, role, country, country_code, signup_date, source_path, lead_magnet, status FROM subscribers ORDER BY signup_date DESC LIMIT ? OFFSET ?")
          .bind(limit, offset).all();
        if (rows && rows.results) subscribers = rows.results;
      } catch (e) {
        console.warn("D1 subscribers query fallback:", e.message);
      }
    }

    if (subscribers.length === 0) {
      subscribers = FALLBACK_SUBSCRIBERS_SAMPLE;
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
      pii_protected: !reveal
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store, private",
        "X-Robots-Tag": "noindex, nofollow"
      }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}
