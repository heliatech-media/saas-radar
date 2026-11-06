/**
 * Cloudflare Pages Function: /api/sentinel/radar
 * Market Radar & Trend Scout Detection Ledger.
 * Supports GET (list trends) and POST (schedule editorial brief for ContentWriter).
 */

const RADAR_ITEMS = [
  { tool_name: "Cursor 0.43", slug: "cursor", category: "Developer Tools", velocity_score: "98%", monthly_searches: "~140,000", status: "COVERED", teardown_url: "/blog/cursor-evolution-guide-2026/" },
  { tool_name: "Windsurf 1.2", slug: "windsurf", category: "Developer Tools", velocity_score: "94%", monthly_searches: "~85,000", status: "DUEL_READY", teardown_url: "/blog/cursor-vs-windsurf-2026-claude-3-7-token-limit-pricing-leak/" },
  { tool_name: "v0 by Vercel", slug: "v0", category: "Frontend Generation", velocity_score: "91%", monthly_searches: "~65,000", status: "COVERED", teardown_url: "/reviews/v0/" },
  { tool_name: "Lovable.dev", slug: "lovable", category: "Full-Stack AI", velocity_score: "89%", monthly_searches: "~50,000", status: "COVERED", teardown_url: "/blog/lovable-evolution-guide-2026/" },
  { tool_name: "ElevenAgents", slug: "elevenagents", category: "Conversational Voice", velocity_score: "87%", monthly_searches: "~32,000", status: "COVERED", teardown_url: "/blog/elevenagents-ai-receptionist-guide/" },
  { tool_name: "DeepSeek Coder V2", slug: "deepseek-coder", category: "Open Weights", velocity_score: "85%", monthly_searches: "~45,000", status: "ANALYSIS_QUEUED", teardown_url: null }
];

export async function onRequestGet() {
  return new Response(JSON.stringify({ radar_trends: RADAR_ITEMS, total: RADAR_ITEMS.length }), {
    status: 200,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store, private" }
  });
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const { action, tool_slug, tool_name } = body;
    const actorEmail = context.request.headers.get("Cf-Access-Authenticated-User-Email") || "owner@heliatech.online";
    const db = context.env?.DB;

    if (action === "create_editorial_brief") {
      const nowIso = new Date().toISOString();

      if (db) {
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
          VALUES (datetime('now'), ?, 'owner', 'CREATE_EDITORIAL_BRIEF', ?, ?, 'QUEUED', 'ASSIGNED_TO_WRITER', 'sig_brief_created')
        `).bind(
          actorEmail,
          `radar:${tool_slug || 'tool'}`,
          JSON.stringify({ tool_name, tool_slug, assigned_to: ["ContentWriter", "SoftwareAnalyst"], created_at: nowIso })
        ).run();
      }

      return new Response(JSON.stringify({
        success: true,
        tool_slug,
        tool_name,
        created_at: nowIso,
        assigned_agents: ["ContentWriter", "SoftwareAnalyst"],
        message: `Ordre de rédaction d'un guide complet transmis aux agents ContentWriter & SoftwareAnalyst pour '${tool_name}'. Consigné au journal d'audit.`
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
