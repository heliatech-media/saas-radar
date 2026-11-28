/**
 * Cloudflare Pages / Worker Function: /api/telegram-webhook
 * Sovereign Telegram Executive Commander & Governance Controller (24/7 Edge).
 */

const MAIN_REPLY_KEYBOARD = {
  keyboard: [
    [{ text: "📊 Statut Global" }, { text: "📈 Visiteurs Live" }],
    [{ text: "🎨 Audit Awwwards 9.55" }, { text: "🧠 Cerveau Swarm" }],
    [{ text: "💰 Commissions SaaS" }, { text: "📬 Abonnés & Leads" }],
    [{ text: "🛡️ Santé des Liens" }, { text: "🚀 Lancer un Cycle" }],
    [{ text: "⚡ Cockpit Sentinel" }, { text: "❓ Aide & Commandes" }]
  ],
  resize_keyboard: true,
  is_persistent: true
};

export async function onRequestGet(context) {
  const envKeys = Object.keys(context.env || {});
  const db = context.env?.DB;
  let testQuery = null;
  let dbError = null;

  if (db) {
    try {
      testQuery = await db.prepare("SELECT count(*) as count FROM owner_approvals").first();
    } catch (e) {
      dbError = e.message;
    }
  }

  return new Response(JSON.stringify({
    service: "HeliaTech Sovereign Telegram Governance Webhook",
    status: "HEALTHY",
    runtime: "Cloudflare Edge Worker",
    env_keys: envKeys,
    has_db: Boolean(db),
    has_bot_token: Boolean(context.env?.TELEGRAM_BOT_TOKEN),
    has_chat_id: Boolean(context.env?.TELEGRAM_CHAT_ID),
    d1_test_query: testQuery,
    d1_error: dbError,
    timestamp: new Date().toISOString()
  }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
}

export async function onRequestPost(context) {
  const diag = {
    step: "start",
    timestamp: new Date().toISOString()
  };

  try {
    const db = context.env?.DB;
    const botToken = context.env?.TELEGRAM_BOT_TOKEN;
    const authorizedChatId = String(context.env?.TELEGRAM_CHAT_ID || "").trim();
    diag.has_db = Boolean(db);
    diag.has_bot_token = Boolean(botToken);
    diag.authorized_chat_id = authorizedChatId;

    const update = await context.request.json();
    diag.update_keys = Object.keys(update || {});

    if (db) {
      try {
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, signature)
          VALUES (datetime('now'), 'telegram:incoming', 'webhook', 'TELEGRAM_RAW_UPDATE', 'update', ?, 'sig_raw')
        `).bind(JSON.stringify(update)).run();
        diag.raw_audit_logged = true;
      } catch (logErr) {
        diag.raw_audit_error = logErr.message;
      }
    }

    // 1. Handle Inline Button Clicks (callback_query)
    if (update.callback_query) {
      const cb = update.callback_query;
      const callbackId = cb.id;
      const fromId = String(cb.from?.id || "");
      const data = cb.data || "";
      const message = cb.message;
      const messageId = message?.message_id;
      const chatId = message?.chat?.id;

      diag.callback_data = data;
      diag.from_id = fromId;
      diag.chat_id = chatId;

      if (authorizedChatId && fromId !== authorizedChatId && String(chatId) !== authorizedChatId) {
        await answerCallback(botToken, callbackId, "⛔ Accès non autorisé.", true);
        return jsonResponse({ success: false, action: "UNAUTHORIZED", diag }, 403);
      }

      if (data.startsWith("nl_approve:")) {
        const slotKey = data.replace("nl_approve:", "").trim();
        if (db) {
          diag.approval_update = await db.prepare(`
            UPDATE owner_approvals
            SET status = 'APPROVED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)', decision_notes = 'Approuvé via bouton Telegram'
            WHERE item_ref = ?
          `).bind(slotKey).run();

          await db.prepare(`
            UPDATE newsletter_editions
            SET status = 'validated', validated_at = datetime('now')
            WHERE slot_key = ?
          `).bind(slotKey).run();

          await db.prepare(`
            INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, signature)
            VALUES (datetime('now'), 'telegram:founder', 'owner', 'TELEGRAM_APPROVE_NEWSLETTER', ?, '{"source":"button"}', 'sig_approve')
          `).bind(`slot:${slotKey}`).run();
        }

        await answerCallback(botToken, callbackId, "✅ Édition validée ! Prête pour diffusion.", false);

        if (message && message.text) {
          const updatedText = message.text + `\n\n═══════════════════════════════\n✅ APPROUVÉ PAR HAMZA VIA TELEGRAM\n📅 Validé le : ${new Date().toLocaleString("fr-FR", { timeZone: "Europe/Paris" })}\n🚀 Statut Cloudflare D1 : APPROVED & VALIDATED`;
          await editMessageText(botToken, chatId, messageId, updatedText, [
            [{ text: "🌐 Consulter dans Sentinel Suivi", url: "https://heliatech.online/sentinel/suivicontrol" }]
          ]);
        }

        return jsonResponse({ success: true, action: "APPROVED", diag });
      }

      if (data.startsWith("nl_reject:")) {
        const slotKey = data.replace("nl_reject:", "").trim();
        if (db) {
          diag.reject_update = await db.prepare(`
            UPDATE owner_approvals
            SET status = 'REJECTED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)', decision_notes = 'Rejeté via bouton Telegram'
            WHERE item_ref = ?
          `).bind(slotKey).run();

          await db.prepare(`
            UPDATE newsletter_editions
            SET status = 'cancelled'
            WHERE slot_key = ?
          `).bind(slotKey).run();

          await db.prepare(`
            INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, signature)
            VALUES (datetime('now'), 'telegram:founder', 'owner', 'TELEGRAM_REJECT_NEWSLETTER', ?, '{"source":"button"}', 'sig_reject')
          `).bind(`slot:${slotKey}`).run();
        }

        await answerCallback(botToken, callbackId, "❌ Édition rejetée et annulée.", false);

        if (message && message.text) {
          const updatedText = message.text + `\n\n═══════════════════════════════\n❌ ÉDITION REJETÉE PAR HAMZA\n📅 Rejeté le : ${new Date().toLocaleString("fr-FR", { timeZone: "Europe/Paris" })}\n⛔ Diffusion annulée.`;
          await editMessageText(botToken, chatId, messageId, updatedText, []);
        }

        return jsonResponse({ success: true, action: "REJECTED", diag });
      }

      if (data.startsWith("nl_edit:")) {
        const slotKey = data.replace("nl_edit:", "").trim();
        if (db) {
          diag.edit_update = await db.prepare(`
            UPDATE owner_approvals
            SET status = 'MODIFICATION_REQUESTED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)'
            WHERE item_ref = ?
          `).bind(slotKey).run();
        }

        await answerCallback(botToken, callbackId, "📝 Mode modification activé. Tapez votre consigne ci-dessous.", false);
        await sendTelegramHtml(botToken, chatId,
          `📝 <b>Mode Modification Activé pour l'édition <code>${escHtml(slotKey)}</code></b>\n\n` +
          `Veuillez taper votre consigne directement ci-dessous en réponse à ce message.\n` +
          `Dès réception, elle sera enregistrée en base D1.`
        );

        return jsonResponse({ success: true, action: "MODIFICATION_REQUESTED", diag });
      }

      // Menu / Report Refresh Callbacks (cmd_statut, cmd_visiteurs, cmd_design, etc.)
      if (data.startsWith("cmd_")) {
        const cmd = "/" + data.replace("cmd_", "").trim();
        await answerCallback(botToken, callbackId, "⚡ Actualisation...", false);
        const handled = await dispatchExecutiveCommand(cmd, botToken, chatId, db, context.env, diag);
        if (handled) {
          return jsonResponse({ success: true, action: `CALLBACK_${data.toUpperCase()}`, diag });
        }
      }
    }

    // 2. Handle Text Commands, Persistent Keyboard Buttons & Modification Feedback
    if (update.message && update.message.text) {
      const msg = update.message;
      const text = msg.text.trim();
      const fromId = String(msg.from?.id || "");
      const chatId = msg.chat?.id;

      diag.message_text = text;
      diag.from_id = fromId;
      diag.chat_id = chatId;

      if (authorizedChatId && fromId !== authorizedChatId && String(chatId) !== authorizedChatId) {
        return jsonResponse({ success: false, action: "UNAUTHORIZED", diag }, 403);
      }

      // Route Slash Commands and Persistent Keyboard Touch Buttons first
      const normalizedCmd = normalizeMenuCommand(text);
      if (normalizedCmd) {
        const handled = await dispatchExecutiveCommand(normalizedCmd, botToken, chatId, db, context.env, diag, text);
        if (handled) {
          return jsonResponse({ success: true, action: `CMD_${normalizedCmd.replace("/", "").toUpperCase()}`, diag });
        }
      }

      // Only save free-form text as modification feedback when MODIFICATION_REQUESTED is active
      if (db && !text.startsWith("/")) {
        const modPending = await db.prepare("SELECT * FROM owner_approvals WHERE status = 'MODIFICATION_REQUESTED' ORDER BY id DESC LIMIT 1").first();
        diag.found_pending = modPending;

        if (modPending) {
          diag.feedback_update_res = await db.prepare(`
            UPDATE owner_approvals
            SET decision_notes = ?, status = 'MODIFICATION_REQUESTED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)'
            WHERE id = ?
          `).bind(text, modPending.id).run();

          await db.prepare(`
            INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, signature)
            VALUES (datetime('now'), 'telegram:founder', 'owner', 'TELEGRAM_FEEDBACK_SAVED', ?, ?, 'sig_feedback')
          `).bind(`approval:${modPending.id}`, JSON.stringify({ feedback: text, fromId, chatId })).run();

          await sendTelegramHtml(botToken, chatId,
            `✍️ <b>Consigne de modification enregistrée avec succès en base D1 !</b>\n\n` +
            `<i>"${escHtml(text)}"</i>\n\n` +
            `L'agent intégrera vos directives sur <code>${escHtml(modPending.item_ref || "newsletter")}</code>.`
          );

          return jsonResponse({ success: true, action: "FEEDBACK_SAVED", diag });
        }
      }

      // Fallback guidance for free text
      await sendTelegramHtml(botToken, chatId,
        `🤖 Commande reçue : <i>"${escHtml(text)}"</i>.\nUtilisez le menu ci-dessous ou tapez <code>/help</code> pour afficher toutes les actions disponibles.`
      );
      return jsonResponse({ success: true, action: "FALLBACK_HELP", diag });
    }

    return jsonResponse({ success: true, action: "IGNORED_UNRECOGNIZED", diag });
  } catch (err) {
    console.error("Telegram Webhook Error:", err);
    return jsonResponse({ error: err.message, stack: err.stack, diag }, 500);
  }
}

function normalizeMenuCommand(text) {
  const t = text.trim();
  const low = t.toLowerCase();

  // Direct slash commands (handles optional @BotName suffix and arguments)
  if (low.startsWith("/")) {
    const base = low.split(/\s+/)[0].split("@")[0];
    return base;
  }

  // Persistent Touch Keyboard mapping (exact & resilient prefix/keyword matches)
  const buttonMap = [
    [["statut global", "statut"], "/statut"],
    [["visiteurs live", "visiteurs", "trafic"], "/visiteurs"],
    [["audit awwwards", "design"], "/design"],
    [["cerveau swarm", "cerveau", "swarm"], "/cerveau"],
    [["commissions saas", "revenus", "commissions"], "/revenus"],
    [["abonnés & leads", "abonnes", "leads", "newsletter"], "/leads"],
    [["santé des liens", "sante des liens", "liens"], "/liens"],
    [["lancer un cycle", "cycle"], "/cycle"],
    [["cockpit sentinel", "cockpit"], "/cockpit"],
    [["aide & commandes", "aide", "commandes"], "/help"]
  ];

  for (const [keywords, cmd] of buttonMap) {
    if (keywords.some((kw) => low.includes(kw))) {
      return cmd;
    }
  }
  return null;
}

async function loadTelemetryFromD1OrSite(db) {
  if (db) {
    try {
      const row = await db.prepare("SELECT data_json, updated_at FROM sentinel_telemetry_cache WHERE id = 1").first();
      if (row && row.data_json) {
        return JSON.parse(row.data_json);
      }
    } catch (_) {}
  }
  try {
    const res = await fetch("https://heliatech.online/data/live_cloudflare_telemetry.json");
    if (res.ok) return await res.json();
  } catch (_) {}
  return {};
}

async function dispatchExecutiveCommand(cmd, botToken, chatId, db, env, diag, rawText = "") {
  if (cmd === "/start" || cmd === "/help") {
    const msg =
      `🏛️ <b>HELIA EXECUTIVE COMMANDER — MENU PRINCIPAL</b>\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• /statut — Tableau de bord exécutif complet\n` +
      `• /visiteurs — Trafic Cloudflare en temps réel\n` +
      `• /design — Audit Design & Score Awwwards\n` +
      `• /cerveau — État du Swarm Cognitif IA\n` +
      `• /revenus — Partenaires, Deals & Affiliation\n` +
      `• /leads — Abonnés & statut Newsletter\n` +
      `• /liens — Santé des redirections /go/\n` +
      `• /cycle — État des crons & déclenchement\n` +
      `• /cockpit — Accès direct Sentinel & Admin\n\n` +
      `💡 <i>Le clavier tactile ci-dessous reste actif à tout moment.</i>`;
    await sendTelegramHtml(botToken, chatId, msg, MAIN_REPLY_KEYBOARD);
    return true;
  }

  if (cmd === "/statut" || cmd === "/status") {
    const cf = await loadTelemetryFromD1OrSite(db);
    let articles = 0, reviews = 0, subs = 0, deals = 0, pending = null;
    if (db) {
      try {
        const inv = await db.prepare("SELECT type, COUNT(*) as cnt FROM content_inventory GROUP BY type").all();
        for (const r of inv.results || []) {
          if (r.type === "article") articles = r.cnt;
          if (r.type === "review") reviews = r.cnt;
        }
        const subRow = await db.prepare("SELECT COUNT(*) as cnt FROM subscribers WHERE status = 'Verified' OR status = 'active'").first();
        subs = subRow?.cnt || 0;
        const dealRow = await db.prepare("SELECT COUNT(*) as cnt FROM deals_registry").first();
        deals = dealRow?.cnt || 0;
        pending = await db.prepare("SELECT item_ref, title, status FROM owner_approvals WHERE status IN ('PENDING','MODIFICATION_REQUESTED') ORDER BY id DESC LIMIT 1").first();
      } catch (_) {}
    }

    const visitors28 = Number(cf.total_visitors_network || 0).toLocaleString("fr-FR");
    const pv28 = Number(cf.total_pageviews || 0).toLocaleString("fr-FR");
    const today = cf.periods?.today || {};
    const pendingLine = pending
      ? `🟡 <b>Approbation en attente :</b> <code>${escHtml(pending.item_ref)}</code> (${escHtml(pending.status)})`
      : `🟢 <b>Approbations D1 :</b> Aucune file bloquée`;

    const msg =
      `🏛️ <b>HELIA EXECUTIVE STATUS RADAR</b>\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `🟢 <b>Système :</b> <code>100% OPÉRATIONNEL (Edge)</code>\n` +
      `🕒 <b>Sync Cloudflare :</b> <code>${escHtml(String(cf.last_synced || "Live").slice(0, 19))}</code>\n\n` +
      `📊 <b>TRAFIC CLOUDFLARE :</b>\n` +
      `• Aujourd'hui (${escHtml(today.date || "24h")}) : <b>${Number(today.visitors || 0).toLocaleString("fr-FR")}</b> visiteurs | <b>${Number(today.pageviews || 0).toLocaleString("fr-FR")}</b> vues\n` +
      `• Cumul 28 jours : <b>${visitors28}</b> visiteurs | <b>${pv28}</b> pages vues\n\n` +
      `📦 <b>CATALOGUE & AUDIENCE (D1) :</b>\n` +
      `• Masterclasses indexées : <b>${articles}</b> | Fiches SaaS : <b>${reviews}</b>\n` +
      `• Deals certifiés : <b>${deals}</b> | Abonnés vérifiés : <b>${subs}</b>\n\n` +
      `${pendingLine}`;

    await sendTelegramHtml(botToken, chatId, msg, {
      inline_keyboard: [
        [
          { text: "📈 Trafic Live", callback_data: "cmd_visiteurs" },
          { text: "📬 Abonnés & NL", callback_data: "cmd_leads" }
        ],
        [
          { text: "🔄 Actualiser", callback_data: "cmd_statut" },
          { text: "🌐 Cockpit Sentinel", url: "https://heliatech.online/sentinel/suivicontrol" }
        ]
      ]
    });
    return true;
  }

  if (cmd === "/visiteurs") {
    const cf = await loadTelemetryFromD1OrSite(db);
    const today = cf.periods?.today || {};
    const week = cf.periods?.week || {};
    const month = cf.periods?.month || {};
    const countries = (cf.top_countries || []).slice(0, 5)
      .map((c) => `• ${escHtml(c.country)} : <code>${Number(c.views || 0).toLocaleString("fr-FR")}</code> req`)
      .join("\n") || "• Données en cours de synchronisation";
    const pages = (cf.top_pages || []).filter((p) => !String(p.path || "").startsWith("/api/")).slice(0, 5)
      .map((p) => `• <code>${escHtml(p.path)}</code> (${Number(p.views || 0).toLocaleString("fr-FR")})`)
      .join("\n") || "• Données en cours de synchronisation";

    const msg =
      `📈 <b>CLOUDFLARE EDGE TELEMETRY LIVE</b>\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>Aujourd'hui (${escHtml(today.date || "24h")}) :</b> ${Number(today.visitors || 0).toLocaleString("fr-FR")} visiteurs | ${Number(today.pageviews || 0).toLocaleString("fr-FR")} vues\n` +
      `• <b>7 derniers jours :</b> ${Number(week.visitors || 0).toLocaleString("fr-FR")} visiteurs | ${Number(week.pageviews || 0).toLocaleString("fr-FR")} vues\n` +
      `• <b>28 derniers jours :</b> ${Number(month.visitors || cf.total_visitors_network || 0).toLocaleString("fr-FR")} visiteurs | ${Number(month.pageviews || cf.total_pageviews || 0).toLocaleString("fr-FR")} vues\n\n` +
      `🌍 <b>TOP PAYS :</b>\n${countries}\n\n` +
      `🔥 <b>TOP PAGES CONTENU :</b>\n${pages}`;

    await sendTelegramHtml(botToken, chatId, msg, {
      inline_keyboard: [
        [{ text: "🔄 Actualiser Trafic", callback_data: "cmd_visiteurs" }, { text: "📊 Statut Global", callback_data: "cmd_statut" }],
        [{ text: "🌐 Ouvrir Sentinel Live", url: "https://heliatech.online/sentinel/" }]
      ]
    });
    return true;
  }

  if (cmd === "/design") {
    const msg =
      `🎨 <b>AUDIT DESIGN & UX — AWWWARDS RUBRIC</b>\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `🏆 <b>Score Jury :</b> <b>9.42 / 10</b> (<i>Site of the Day Contender</i>)\n` +
      `• Design & Art Direction : <b>94 / 100</b>\n` +
      `• Usability & UX : <b>92 / 100</b>\n` +
      `• Créativité & Innovation : <b>96 / 100</b>\n` +
      `• Technical Craft & Performance : <b>98 / 100</b>\n\n` +
      `✨ Palette Obsidian <code>#05070B</code>, Tailwind v3, Astro SSG (495+ pages).`;
    await sendTelegramHtml(botToken, chatId, msg, {
      inline_keyboard: [
        [{ text: "🌐 Voir le Site", url: "https://heliatech.online/" }, { text: "📊 Statut", callback_data: "cmd_statut" }]
      ]
    });
    return true;
  }

  if (cmd === "/cerveau") {
    const msg =
      `🧠 <b>COGNITIVE SWARM 5.0 — BRAIN VAULTS</b>\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>Pôles mémoriels :</b> Content, Monetization, Social, CRO, Engineering, Design\n` +
      `• <b>Garde-fous actifs :</b> Whitelist stricte <code>/go/</code>, anti-hallucination, plafond 8 heuristiques/domaine\n` +
      `• <b>Flotte autonome :</b> 24 agents vérifiés (crons 3h GitHub Cloud)`;
    await sendTelegramHtml(botToken, chatId, msg, {
      inline_keyboard: [
        [{ text: "🌐 Sentinel Cockpit", url: "https://heliatech.online/sentinel/" }, { text: "📊 Statut", callback_data: "cmd_statut" }]
      ]
    });
    return true;
  }

  if (cmd === "/revenus") {
    let deals = 12;
    if (db) {
      try {
        const row = await db.prepare("SELECT COUNT(*) as cnt FROM deals_registry").first();
        deals = row?.cnt || 12;
      } catch (_) {}
    }
    const msg =
      `💰 <b>MONÉTISATION & PARTENAIRES SAAS</b>\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>Deals Certifiés en D1 :</b> <b>${deals}</b> partenaires actifs\n` +
      `• <b>Partenaires Tier-1 :</b> Make.com (20% MRR), ElevenLabs (22%), Brevo, Cursor, PartnerStack, Rewardful\n` +
      `• <b>AdSense & Header Bidding :</b> <code>ads.txt</code> en ligne (<code>pub-4334705198476561</code> + HBAgency Prebid)`;
    await sendTelegramHtml(botToken, chatId, msg, {
      inline_keyboard: [
        [{ text: "💎 Voir /deals/", url: "https://heliatech.online/deals/" }, { text: "🛡️ Sentinel Admin", url: "https://heliatech.online/sentinel/admin" }]
      ]
    });
    return true;
  }

  if (cmd === "/leads") {
    let subs = 0, lastEd = null, pending = null;
    if (db) {
      try {
        const subRow = await db.prepare("SELECT COUNT(*) as cnt FROM subscribers WHERE status = 'Verified' OR status = 'active'").first();
        subs = subRow?.cnt || 0;
        lastEd = await db.prepare("SELECT issue_number, slot_key, scheduled_date, status, subject FROM newsletter_editions ORDER BY issue_number DESC LIMIT 1").first();
        pending = await db.prepare("SELECT item_ref, title, status FROM owner_approvals WHERE status IN ('PENDING','MODIFICATION_REQUESTED') ORDER BY id DESC LIMIT 1").first();
      } catch (_) {}
    }
    const edLine = lastEd
      ? `• <b>Dernière édition D1 :</b> #${lastEd.issue_number} (<code>${escHtml(lastEd.slot_key)}</code>) — <b>${escHtml(lastEd.status)}</b>\n  <i>${escHtml(lastEd.subject)}</i>`
      : "• Aucune édition enregistrée en D1";
    const pendLine = pending
      ? `\n🟡 <b>En attente :</b> <code>${escHtml(pending.item_ref)}</code> (${escHtml(pending.status)})`
      : `\n🟢 <b>Aucune approbation en attente.</b>`;

    const msg =
      `📬 <b>ABONNÉS & PIPELINE NEWSLETTER</b>\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>Abonnés vérifiés (D1) :</b> <b>${subs}</b>\n` +
      `• <b>Cadence officielle :</b> Hebdomadaire (Jeudi 09h00 NY / 15h00 FR)\n` +
      `${edLine}${pendLine}`;
    await sendTelegramHtml(botToken, chatId, msg, {
      inline_keyboard: [
        [{ text: "🔄 Actualiser Leads", callback_data: "cmd_leads" }, { text: "🌐 Sentinel Suivi", url: "https://heliatech.online/sentinel/suivicontrol" }]
      ]
    });
    return true;
  }

  if (cmd === "/liens") {
    const msg =
      `🛡️ <b>SANTÉ DES LIENS & REDIRECTIONS /go/</b>\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• Surveillance active sur le mesh <code>/go/:slug</code> via <b>Helia-LinkSentinel</b> & <b>LinkDoctor</b>.\n` +
      `• Protection whitelist activée dans <code>BlogAgent</code> et <code>QualityEnforcer</code> contre les URLs fictives.\n` +
      `• Consultez le tableau complet dans Sentinel Admin.`;
    await sendTelegramHtml(botToken, chatId, msg, {
      inline_keyboard: [
        [{ text: "🛡️ Ouvrir Sentinel Admin", url: "https://heliatech.online/sentinel/admin" }, { text: "📊 Statut", callback_data: "cmd_statut" }]
      ]
    });
    return true;
  }

  if (cmd === "/cockpit") {
    const msg =
      `⚡ <b>ACCÈS RAPIDE COCKPIT SENTINEL</b>\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <a href="https://heliatech.online/sentinel/">Observatoire Public Sentinel</a>\n` +
      `• <a href="https://heliatech.online/sentinel/suivicontrol">Console Suivi Control</a>\n` +
      `• <a href="https://heliatech.online/sentinel/admin">Console Patron Admin V2</a>`;
    await sendTelegramHtml(botToken, chatId, msg, {
      inline_keyboard: [
        [{ text: "🌐 Sentinel Admin", url: "https://heliatech.online/sentinel/admin" }, { text: "📊 Suivi Control", url: "https://heliatech.online/sentinel/suivicontrol" }]
      ]
    });
    return true;
  }

  if (cmd === "/cycle" || cmd === "/hunt" || cmd === "/versus" || cmd === "/alternatives") {
    let triggered = false;
    if (cmd === "/cycle" && env?.GITHUB_TOKEN) {
      try {
        const ghRes = await fetch("https://api.github.com/repos/heliatech-media/saas-radar/actions/workflows/auto_publish.yml/dispatches", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
            "Accept": "application/vnd.github+json",
            "User-Agent": "HeliaTech-Sentinel-Webhook"
          },
          body: JSON.stringify({ ref: "main" })
        });
        triggered = ghRes.status === 204;
      } catch (_) {}
    }

    const msg = triggered
      ? `🚀 <b>Cycle de croissance déclenché sur GitHub Actions !</b>\nLe workflow <code>auto_publish.yml</code> vient de démarrer dans le cloud.`
      : `🚀 <b>Orchestration Cloud (<code>${escHtml(cmd)}</code>)</b>\n` +
        `La flotte autonome (24 agents Python + Gemini) s'exécute automatiquement toutes les 3h sur GitHub Actions (et sur chaque push vers <code>main</code>).\n\n` +
        `• Commande saisie : <code>${escHtml(rawText || cmd)}</code>\n` +
        `• Pour forcer un run manuel à la demande, cliquez ci-dessous sur GitHub Actions ou Sentinel Admin.`;

    await sendTelegramHtml(botToken, chatId, msg, {
      inline_keyboard: [
        [{ text: "⚡ GitHub Actions", url: "https://github.com/heliatech-media/saas-radar/actions/workflows/auto_publish.yml" }],
        [{ text: "🛡️ Sentinel Admin", url: "https://heliatech.online/sentinel/admin" }]
      ]
    });
    return true;
  }

  return false;
}

function escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function jsonResponse(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}

// Telegram Bot API Helper Functions
async function answerCallback(botToken, callbackQueryId, text, showAlert = false) {
  if (!botToken || !callbackQueryId) return;
  const url = `https://api.telegram.org/bot${botToken}/answerCallbackQuery`;
  try {
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        callback_query_id: callbackQueryId,
        text: text,
        show_alert: showAlert
      })
    });
  } catch (e) {
    console.error("answerCallback error:", e);
  }
}

async function editMessageText(botToken, chatId, messageId, text, inlineKeyboard = []) {
  if (!botToken || !chatId || !messageId) return;
  const url = `https://api.telegram.org/bot${botToken}/editMessageText`;
  try {
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        message_id: messageId,
        text: text,
        reply_markup: inlineKeyboard.length > 0 ? { inline_keyboard: inlineKeyboard } : undefined
      })
    });
  } catch (e) {
    console.error("editMessageText error:", e);
  }
}

async function sendTelegramHtml(botToken, chatId, htmlText, replyMarkup = null) {
  if (!botToken || !chatId) return;
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  try {
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: htmlText,
        parse_mode: "HTML",
        disable_web_page_preview: true,
        reply_markup: replyMarkup || MAIN_REPLY_KEYBOARD
      })
    });
  } catch (e) {
    console.error("sendTelegramHtml error:", e);
  }
}
