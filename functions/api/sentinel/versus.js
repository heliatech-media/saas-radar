/**
 * Cloudflare Pages Function: /api/sentinel/versus
 * 31 Head-to-Head Comparison Duels Matrix.
 */

const SAMPLE_VERSUS = [
  { duel_slug: "cursor-vs-github-copilot", tool_a: "Cursor", tool_b: "GitHub Copilot", winner_tool: "Cursor", category: "Developer Tools", tco_delta: "+42% Velocity", last_benchmarked_at: "2026-11-06T12:00:00Z", status: "ACTIVE" },
  { duel_slug: "make-vs-zapier", tool_a: "Make.com", tool_b: "Zapier", winner_tool: "Make.com", category: "Automation", tco_delta: "-68% en volume", last_benchmarked_at: "2026-11-06T12:00:00Z", status: "ACTIVE" },
  { duel_slug: "apollo-io-vs-zoominfo", tool_a: "Apollo.io", tool_b: "ZoomInfo", winner_tool: "Apollo.io", category: "Sales Intelligence", tco_delta: "-74% Annuel", last_benchmarked_at: "2026-11-06T12:00:00Z", status: "ACTIVE" },
  { duel_slug: "typeform-vs-tally", tool_a: "Typeform", tool_b: "Tally", winner_tool: "Tally", category: "Forms & Surveys", tco_delta: "99% d'économies", last_benchmarked_at: "2026-11-06T12:00:00Z", status: "ACTIVE" },
  { duel_slug: "supabase-vs-firebase", tool_a: "Supabase", tool_b: "Firebase", winner_tool: "Supabase", category: "Backend Infrastructure", tco_delta: "-60% Egress Data", last_benchmarked_at: "2026-11-06T12:00:00Z", status: "ACTIVE" }
];

export async function onRequestGet(context) {
  try {
    const db = context.env?.DB;
    let duels = [];

    if (db) {
      try {
        const rows = await db.prepare("SELECT * FROM versus_matrix ORDER BY duel_slug ASC").all();
        if (rows && rows.results && rows.results.length > 0) duels = rows.results;
      } catch (e) {
        console.warn("D1 versus fallback:", e.message);
      }
    }

    if (duels.length === 0) duels = SAMPLE_VERSUS;

    return new Response(JSON.stringify({ duels, total: duels.length }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}
