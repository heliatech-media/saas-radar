/**
 * Cloudflare Pages Function: /api/sentinel/crons
 * Supervision & Déclenchement Réel des Workflows GitHub Actions.
 * ZÉRO SIMULATION : Si GITHUB_DISPATCH_TOKEN est configuré, déclenche réellement
 * l'API GitHub Actions workflow_dispatch via HTTP POST.
 */

const WORKFLOW_MAP = {
  "auto_publish": "auto_publish.yml",
  "daily_health_check": "daily_health_check.yml",
  "deal_probe_48h": "deal_probe.yml",
  "newsletter_engine": "newsletter_draft.yml",
  "trend_scout": "trend_scout.yml",
  "audit_backup_r2": "audit_backup.yml"
};

export async function onRequestGet(context) {
  try {
    const db = context.env?.DB;
    let isFleetPaused = false;

    if (db) {
      try {
        const row = await db.prepare("SELECT fleet_status FROM fleet_controls WHERE id = 1").first();
        if (row && row.fleet_status === "PAUSED") isFleetPaused = true;
      } catch (e) {
        console.warn("D1 fleet check:", e.message);
      }
    }

    const crons = [
      {
        id: "auto_publish",
        name: "Cycle Éditorial & Radar (3h)",
        workflow_file: "auto_publish.yml",
        source: "Workflow .github/workflows/auto_publish.yml",
        cron_expression: "0 */3 * * *",
        cadence_label: "Toutes les 3 heures",
        runner: "ubuntu-latest",
        last_run_status: isFleetPaused ? "PAUSED_BY_OWNER" : "ACTIVE",
        kill_switch_compliance: "Respecte fleet_controls.fleet_status = PAUSED"
      },
      {
        id: "daily_health_check",
        name: "Inspection Quotidienne & Liens Affiliés (4h UTC)",
        workflow_file: "daily_health_check.yml",
        source: "Workflow .github/workflows/daily_health_check.yml",
        cron_expression: "0 4 * * *",
        cadence_label: "Quotidien à 04:00 UTC",
        runner: "ubuntu-latest",
        last_run_status: "ACTIVE",
        kill_switch_compliance: "SecurityAgent et audits d'intégrité non suspensibles"
      },
      {
        id: "deal_probe_48h",
        name: "Sondage Technique des Deals 48h",
        workflow_file: "deal_probe.yml",
        source: "Workflow .github/workflows/deal_probe.yml",
        cron_expression: "0 */6 * * *",
        cadence_label: "Toutes les 6 heures",
        runner: "ubuntu-latest",
        last_run_status: "ACTIVE",
        kill_switch_compliance: "Sonde technique sans modification commerciale"
      },
      {
        id: "newsletter_engine",
        name: "Générateur Brouillon Newsletter (Mardi & Jeudi)",
        workflow_file: "newsletter_draft.yml",
        source: "Workflow .github/workflows/newsletter_draft.yml",
        cron_expression: "0 9 * * 2,4",
        cadence_label: "Mardi & Jeudi à 09:00 NY",
        runner: "ubuntu-latest",
        last_run_status: "ACTIVE",
        kill_switch_compliance: "Verrou DRAFT_LOCKED : validation patron requise"
      },
      {
        id: "trend_scout",
        name: "Radar de Veille & Signaux Faibles (6h)",
        workflow_file: "trend_scout.yml",
        source: "Workflow .github/workflows/trend_scout.yml",
        cron_expression: "0 */6 * * *",
        cadence_label: "Toutes les 6 heures",
        runner: "ubuntu-latest",
        last_run_status: isFleetPaused ? "PAUSED_BY_OWNER" : "ACTIVE",
        kill_switch_compliance: "Respecte fleet_controls.fleet_status = PAUSED"
      },
      {
        id: "audit_backup_r2",
        name: "Sauvegarde Immuable D1 & Points de Contrôle R2 (WORM)",
        workflow_file: "audit_backup.yml",
        source: "Workflow .github/workflows/audit_backup.yml",
        cron_expression: "0 0 * * *",
        cadence_label: "Quotidien à 00:00 UTC",
        runner: "ubuntu-latest",
        last_run_status: "ACTIVE",
        kill_switch_compliance: "Sauvegarde continue non suspensible"
      }
    ];

    return new Response(JSON.stringify({
      crons,
      total_crons: crons.length,
      fleet_paused: isFleetPaused,
      governance_rule: "Verrou strict d'exécution unique."
    }), {
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
    const { action, cron_id } = body;
    const actorEmail = context.request.headers.get("Cf-Access-Authenticated-User-Email") || "owner@heliatech.online";
    const db = context.env?.DB;
    const ghToken = context.env?.GITHUB_DISPATCH_TOKEN || context.env?.GITHUB_TOKEN || context.env?.GH_TOKEN;

    if (action === "trigger_run") {
      const nowIso = new Date().toISOString();
      const targetCron = cron_id || "auto_publish";
      const workflowFile = WORKFLOW_MAP[targetCron] || `${targetCron}.yml`;
      let dispatchResult = { success: false, mode: "d1_only", message: "" };

      // 1. Déclenchement réel GitHub Actions via workflow_dispatch API
      if (ghToken) {
        try {
          const ghUrl = `https://api.github.com/repos/heliatech-media/saas-radar/actions/workflows/${workflowFile}/dispatches`;
          const ghRes = await fetch(ghUrl, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${ghToken}`,
              "Accept": "application/vnd.github+json",
              "User-Agent": "HeliaTech-SentinelAdmin/2.4",
              "X-GitHub-Api-Version": "2022-11-28"
            },
            body: JSON.stringify({ ref: "main" })
          });

          if (ghRes.status === 204) {
            dispatchResult = {
              success: true,
              mode: "github_api_dispatched",
              status_code: 204,
              message: `Workflow GitHub Actions '${workflowFile}' déclenché en production avec succès (HTTP 204).`
            };
          } else {
            const errText = await ghRes.text();
            dispatchResult = {
              success: false,
              mode: "github_api_error",
              status_code: ghRes.status,
              message: `Réponse GitHub API HTTP ${ghRes.status} : ${errText.substring(0, 200)}`
            };
          }
        } catch (ghErr) {
          dispatchResult = {
            success: false,
            mode: "github_api_exception",
            message: `Erreur d'appel GitHub API : ${ghErr.message}`
          };
        }
      } else {
        dispatchResult = {
          success: true,
          mode: "d1_audit_logged",
          message: `Signal consigné en D1. Pour le déclenchement distant automatique du runner GitHub, configurez GITHUB_DISPATCH_TOKEN dans les variables Cloudflare Pages.`
        };
      }

      // 2. Consigner l'ordre patron dans le journal d'audit immuable D1
      if (db) {
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
          VALUES (datetime('now'), ?, 'owner', 'CRON_MANUAL_DISPATCH', ?, ?, 'SCHEDULED', 'DISPATCHED', 'sig_manual_cron')
        `).bind(
          actorEmail,
          `cron:${targetCron}`,
          JSON.stringify({ actorEmail, cron_id: targetCron, workflow_file: workflowFile, triggered_at: nowIso, dispatch_mode: dispatchResult.mode })
        ).run();
      }

      return new Response(JSON.stringify({
        success: dispatchResult.success,
        cron_id: targetCron,
        workflow_file: workflowFile,
        triggered_at: nowIso,
        actor: actorEmail,
        dispatch_mode: dispatchResult.mode,
        message: dispatchResult.message
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
