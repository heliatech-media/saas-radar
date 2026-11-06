/**
 * Cloudflare Pages Function: /api/sentinel/fleet
 * Master Fleet Controls: PAUSE ALL AGENTS, RESUME, and individual agent toggles.
 * Exemption rule: SecurityAgent, MarketplaceSecuritySentinel, and NotifierAgent CANNOT be suspended.
 */

const EXEMPT_AGENTS = ["SecurityAgent", "MarketplaceSecuritySentinel", "NotifierAgent"];

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

    if (action === "pause") {
      if (db) {
        await db.prepare("UPDATE fleet_controls SET fleet_status = 'PAUSED', last_updated_at = datetime('now'), last_updated_by = ? WHERE id = 1").bind(actorEmail).run();
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
          VALUES (datetime('now'), ?, 'owner', 'PAUSE_ALL_AGENTS', 'fleet', '{"exempt_kept_active":["SecurityAgent","MarketplaceSecuritySentinel","NotifierAgent"]}', 'RUNNING', 'PAUSED', 'sig_pause_verified')
        `).bind(actorEmail).run();
      }
      result = {
        success: true,
        fleet_status: "PAUSED",
        message: "Tous les agents non critiques sont suspendus. SecurityAgent et alertes restent 100% actifs.",
        exempt_agents_active: EXEMPT_AGENTS
      };
    } else if (action === "resume") {
      if (db) {
        await db.prepare("UPDATE fleet_controls SET fleet_status = 'RUNNING', last_updated_at = datetime('now'), last_updated_by = ? WHERE id = 1").bind(actorEmail).run();
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
          VALUES (datetime('now'), ?, 'owner', 'RESUME_ALL_AGENTS', 'fleet', '{"reason":"Owner clicked resume"}', 'PAUSED', 'RUNNING', 'sig_resume_verified')
        `).bind(actorEmail).run();
      }
      result = {
        success: true,
        fleet_status: "RUNNING",
        message: "La flotte d'agents est réactivée."
      };
    } else if (action === "toggle-agent") {
      const agentName = body.agent_name;
      if (!agentName) {
        return new Response(JSON.stringify({ error: "agent_name required" }), { status: 400 });
      }

      if (EXEMPT_AGENTS.includes(agentName)) {
        return new Response(JSON.stringify({
          error: `Sécurité Violation: L'agent '${agentName}' est protégé et non-suspensible.`
        }), { status: 403 });
      }

      let suspended = [];
      if (db) {
        const fc = await db.prepare("SELECT suspended_agents FROM fleet_controls WHERE id = 1").first();
        if (fc && fc.suspended_agents) {
          try { suspended = JSON.parse(fc.suspended_agents); } catch (e) {}
        }
      }

      let nowSuspended = false;
      if (suspended.includes(agentName)) {
        suspended = suspended.filter(a => a !== agentName);
        nowSuspended = false;
      } else {
        suspended.push(agentName);
        nowSuspended = true;
      }

      if (db) {
        await db.prepare("UPDATE fleet_controls SET suspended_agents = ?, last_updated_at = datetime('now'), last_updated_by = ? WHERE id = 1").bind(JSON.stringify(suspended), actorEmail).run();
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
          VALUES (datetime('now'), ?, 'owner', 'TOGGLE_AGENT', ?, ?, ?, ?, 'sig_agent_toggle')
        `).bind(actorEmail, `agent:${agentName}`, JSON.stringify({ suspended: nowSuspended }), nowSuspended ? "ACTIVE" : "SUSPENDED", nowSuspended ? "SUSPENDED" : "ACTIVE").run();
      }

      result = {
        success: true,
        agent_name: agentName,
        is_suspended: nowSuspended,
        message: nowSuspended ? `Agent ${agentName} suspendu.` : `Agent ${agentName} réactivé.`
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
