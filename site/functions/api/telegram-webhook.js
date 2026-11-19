/**
 * Cloudflare Pages Function: /api/telegram-webhook
 * Autonomous Telegram Human-in-the-Loop Governance Controller.
 * Handles interactive inline keyboard approvals & modification feedback directly from Hamza's Telegram.
 */

export async function onRequestGet(context) {
  return new Response(JSON.stringify({
    service: "HeliaTech Sovereign Telegram Governance Webhook",
    status: "HEALTHY",
    runtime: "Cloudflare Edge Worker",
    timestamp: new Date().toISOString()
  }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
}

export async function onRequestPost(context) {
  try {
    const db = context.env?.DB;
    const botToken = context.env?.TELEGRAM_BOT_TOKEN;
    const authorizedChatId = String(context.env?.TELEGRAM_CHAT_ID || "");

    const update = await context.request.json();

    // 0. Always persist raw incoming update to D1 audit logs for forensic visibility
    if (db) {
      try {
        await db.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
          VALUES (datetime('now'), 'telegram:incoming', 'webhook', 'TELEGRAM_INCOMING_RAW', 'update', ?, '', '', 'sig_raw')
        `).bind(JSON.stringify(update)).run();
      } catch (logErr) {
        console.error("Error logging raw update to D1:", logErr);
      }
    }

    // 1. Handle Inline Button Clicks (callback_query)
    if (update.callback_query) {
      const cb = update.callback_query;
      const callbackId = cb.id;
      const fromId = String(cb.from?.id);
      const data = cb.data || "";
      const message = cb.message;
      const messageId = message?.message_id;
      const chatId = message?.chat?.id;

      // Generous authorization: match fromId or chatId or authorizedChatId
      const isAuth = !authorizedChatId || fromId === authorizedChatId || String(chatId) === authorizedChatId || authorizedChatId.includes(fromId);

      if (!isAuth) {
        await answerCallback(botToken, callbackId, "⛔ Accès réservé au fondateur.", true);
        return new Response("OK", { status: 200 });
      }

      if (data.startsWith("nl_approve:")) {
        const slotKey = data.replace("nl_approve:", "").trim();

        if (db) {
          await db.prepare(`
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
            INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
            VALUES (datetime('now'), 'telegram:founder', 'owner', 'TELEGRAM_APPROVE_NEWSLETTER', ?, '{"source":"telegram_inline_button"}', 'PENDING', 'APPROVED', 'sig_tg_approve')
          `).bind(`slot:${slotKey}`).run();
        }

        await answerCallback(botToken, callbackId, "✅ Édition validée ! Prête pour diffusion.", false);

        if (message && message.text) {
          const updatedText = message.text + `\n\n═══════════════════════════════\n✅ **APPROUVÉ PAR HAMZA VIA TELEGRAM**\n📅 Validé le : ${new Date().toLocaleString("fr-FR", { timeZone: "Europe/Paris" })}\n🚀 Statut Cloudflare D1 : APPROVED & VALIDATED`;
          await editMessageText(botToken, chatId, messageId, updatedText, [
            [
              { text: "🌐 Consulter dans Sentinel Suivi", url: "https://heliatech.online/sentinel/suivicontrol" }
            ]
          ]);
        }

        return new Response("OK", { status: 200 });
      }

      if (data.startsWith("nl_reject:")) {
        const slotKey = data.replace("nl_reject:", "").trim();

        if (db) {
          await db.prepare(`
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
            INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
            VALUES (datetime('now'), 'telegram:founder', 'owner', 'TELEGRAM_REJECT_NEWSLETTER', ?, '{"source":"telegram_inline_button"}', 'PENDING', 'REJECTED', 'sig_tg_reject')
          `).bind(`slot:${slotKey}`).run();
        }

        await answerCallback(botToken, callbackId, "❌ Édition rejetée et annulée.", false);

        if (message && message.text) {
          const updatedText = message.text + `\n\n═══════════════════════════════\n❌ **ÉDITION REJETÉE PAR HAMZA**\n📅 Rejeté le : ${new Date().toLocaleString("fr-FR", { timeZone: "Europe/Paris" })}\n⛔ Diffusion annulée.`;
          await editMessageText(botToken, chatId, messageId, updatedText, []);
        }

        return new Response("OK", { status: 200 });
      }

      if (data.startsWith("nl_edit:")) {
        const slotKey = data.replace("nl_edit:", "").trim();

        if (db) {
          await db.prepare(`
            UPDATE owner_approvals 
            SET status = 'MODIFICATION_REQUESTED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)'
            WHERE item_ref = ?
          `).bind(slotKey).run();
        }

        await answerCallback(botToken, callbackId, "📝 Mode modification activé.", false);

        await sendTelegramMessage(botToken, chatId, 
          `📝 **Demande de Modification enregistrée pour l'édition \`${slotKey}\`**\n\n` +
          `Veuillez taper votre consigne directement ci-dessous en réponse à ce message ` +
          `(ex : *"Change le sujet pour X"*, *"Remplace l'outil en spotlight par n8n"*, etc.).\n` +
          `L'agent intégrera vos directives avant de vous soumettre une nouvelle version.`
        );

        return new Response("OK", { status: 200 });
      }
    }

    // 2. Handle Text Messages from the Founder
    if (update.message && update.message.text) {
      const msg = update.message;
      const text = msg.text.trim();
      const fromId = String(msg.from?.id);
      const chatId = msg.chat?.id;

      // Handle /status command
      if (text === "/status") {
        let pendingCount = 0;
        let latestPending = null;
        if (db) {
          const rows = await db.prepare("SELECT * FROM owner_approvals WHERE status = 'PENDING' ORDER BY id DESC LIMIT 1").all();
          if (rows && rows.results && rows.results.length > 0) {
            pendingCount = rows.results.length;
            latestPending = rows.results[0];
          }
        }

        const statusMsg = pendingCount > 0
          ? `⚡ **Sentinel Gouvernance : 1 édition en attente d'approbation !**\n\n• **Créneau :** \`${latestPending.item_ref}\`\n• **Titre :** ${latestPending.title}\n• **Statut :** PENDING 🟡\n\nUtilisez les boutons ci-dessus ou répondez pour valider.`
          : `✅ **Sentinel Gouvernance : Aucun envoi en attente.**\n\nToutes les éditions sont soit archivées, soit diffusées. Prochaine édition programmée selon le calendrier.`;

        await sendTelegramMessage(botToken, chatId, statusMsg);
        return new Response("OK", { status: 200 });
      }

      // If the founder sends feedback or editing instruction
      if (db) {
        const pending = await db.prepare("SELECT * FROM owner_approvals WHERE status IN ('MODIFICATION_REQUESTED', 'PENDING') ORDER BY id DESC LIMIT 1").first();
        if (pending) {
          await db.prepare(`
            UPDATE owner_approvals 
            SET decision_notes = ?, status = 'MODIFICATION_REQUESTED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)'
            WHERE id = ?
          `).bind(text, pending.id).run();

          await db.prepare(`
            INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
            VALUES (datetime('now'), 'telegram:founder', 'owner', 'TELEGRAM_FEEDBACK_SAVED', ?, ?, 'PENDING', 'MODIFICATION_REQUESTED', 'sig_tg_feedback')
          `).bind(`approval:${pending.id}`, JSON.stringify({ feedback: text, fromId, chatId })).run();

          await sendTelegramMessage(botToken, chatId, `✍️ **Consigne de modification enregistrée avec succès en base D1 !**\n\n> *"${text}"*\n\nL'agent adapte immédiatement le contenu.`);
          return new Response("OK", { status: 200 });
        }
      }
    }

    return new Response("OK", { status: 200 });
  } catch (err) {
    console.error("Telegram Webhook Error:", err);
    return new Response(JSON.stringify({ error: err.message }), { status: 500 });
  }
}

// Telegram Bot API Helper Functions
async function answerCallback(botToken, callbackQueryId, text, showAlert = false) {
  if (!botToken || !callbackQueryId) return;
  const url = `https://api.telegram.org/bot${botToken}/answerCallbackQuery`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      callback_query_id: callbackQueryId,
      text: text,
      show_alert: showAlert
    })
  });
}

async function editMessageText(botToken, chatId, messageId, text, inlineKeyboard = []) {
  if (!botToken || !chatId || !messageId) return;
  const url = `https://api.telegram.org/bot${botToken}/editMessageText`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      message_id: messageId,
      text: text,
      parse_mode: "Markdown",
      reply_markup: inlineKeyboard.length > 0 ? { inline_keyboard: inlineKeyboard } : undefined
    })
  });
}

async function sendTelegramMessage(botToken, chatId, text) {
  if (!botToken || !chatId) return;
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: text,
      parse_mode: "Markdown"
    })
  });
}
