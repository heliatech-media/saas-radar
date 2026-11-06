/**
 * Cloudflare Pages Function: /api/sentinel/radar
 * Market Radar & Trend Scout Detection Ledger.
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
