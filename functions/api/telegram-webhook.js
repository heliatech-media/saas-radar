/**
 * Cloudflare Pages / Worker Function: /api/telegram-webhook
 * Diagnostic & Sovereign Telegram Governance Controller.
 */

export async function onRequestGet(context) {
  const envKeys = Object.keys(context.env || {});
  const db = context.env?.DB;
  let testQuery = null;
  let dbError = null;

  if (db) {
    try {
      const row = await db.prepare("SELECT count(*) as count FROM owner_approvals").first();
      testQuery = row;
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
    const authorizedChatId = String(context.env?.TELEGRAM_CHAT_ID || "");
    diag.has_db = Boolean(db);
    diag.has_bot_token = Boolean(botToken);
    diag.authorized_chat_id = authorizedChatId;

    const update = await context.request.json();
    diag.update_keys = Object.keys(update || {});

    // Always log raw update to D1 audit logs
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
      const fromId = String(cb.from?.id);
      const data = cb.data || "";
      const message = cb.message;
      const messageId = message?.message_id;
      const chatId = message?.chat?.id;

      diag.callback_data = data;
      diag.from_id = fromId;
      diag.chat_id = chatId;

      if (data.startsWith("nl_approve:")) {
        const slotKey = data.replace("nl_approve:", "").trim();

        if (db) {
          const res1 = await db.prepare(`
            UPDATE owner_approvals 
            SET status = 'APPROVED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)', decision_notes = 'Approuvé via bouton Telegram'
            WHERE item_ref = ?
          `).bind(slotKey).run();
          diag.approval_update = res1;

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
          const updatedText = message.text + `\n\n═══════════════════════════════\n✅ **APPROUVÉ PAR HAMZA VIA TELEGRAM**\n📅 Validé le : ${new Date().toLocaleString("fr-FR", { timeZone: "Europe/Paris" })}\n🚀 Statut Cloudflare D1 : APPROVED & VALIDATED`;
          await editMessageText(botToken, chatId, messageId, updatedText, [
            [
              { text: "🌐 Consulter dans Sentinel Suivi", url: "https://heliatech.online/sentinel/suivicontrol" }
            ]
          ]);
        }

        return new Response(JSON.stringify({ success: true, action: "APPROVED", diag }), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
      }

      if (data.startsWith("nl_reject:")) {
        const slotKey = data.replace("nl_reject:", "").trim();

        if (db) {
          const res2 = await db.prepare(`
            UPDATE owner_approvals 
            SET status = 'REJECTED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)', decision_notes = 'Rejeté via bouton Telegram'
            WHERE item_ref = ?
          `).bind(slotKey).run();
          diag.reject_update = res2;

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
          const updatedText = message.text + `\n\n═══════════════════════════════\n❌ **ÉDITION REJETÉE PAR HAMZA**\n📅 Rejeté le : ${new Date().toLocaleString("fr-FR", { timeZone: "Europe/Paris" })}\n⛔ Diffusion annulée.`;
          await editMessageText(botToken, chatId, messageId, updatedText, []);
        }

        return new Response(JSON.stringify({ success: true, action: "REJECTED", diag }), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
      }

      if (data.startsWith("nl_edit:")) {
        const slotKey = data.replace("nl_edit:", "").trim();

        if (db) {
          const res3 = await db.prepare(`
            UPDATE owner_approvals 
            SET status = 'MODIFICATION_REQUESTED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)'
            WHERE item_ref = ?
          `).bind(slotKey).run();
          diag.edit_update = res3;
        }

        await answerCallback(botToken, callbackId, "📝 Mode modification activé. Tapez votre consigne ci-dessous.", false);

        await sendTelegramMessage(botToken, chatId, 
          `📝 **Mode Modification Activé pour l'édition \`${slotKey}\`**\n\n` +
          `Veuillez taper votre consigne directement ci-dessous en réponse à ce message.\n` +
          `Dès réception, l'agent mettra à jour le contenu.`
        );

        return new Response(JSON.stringify({ success: true, action: "MODIFICATION_REQUESTED", diag }), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
      }
    }

    // 2. Handle Text Messages from the Founder
    if (update.message && update.message.text) {
      const msg = update.message;
      const text = msg.text.trim();
      const fromId = String(msg.from?.id);
      const chatId = msg.chat?.id;

      diag.message_text = text;
      diag.from_id = fromId;
      diag.chat_id = chatId;

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
        return new Response(JSON.stringify({ success: true, action: "STATUS_COMMAND", diag }), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        });
      }

      // Record any incoming feedback message into owner_approvals
      if (db) {
        const pending = await db.prepare("SELECT * FROM owner_approvals WHERE status IN ('MODIFICATION_REQUESTED', 'PENDING') ORDER BY id DESC LIMIT 1").first();
        diag.found_pending = pending;

        if (pending) {
          const updateRes = await db.prepare(`
            UPDATE owner_approvals 
            SET decision_notes = ?, status = 'MODIFICATION_REQUESTED', decided_at = datetime('now'), decided_by = 'Telegram Owner (Hamza)'
            WHERE id = ?
          `).bind(text, pending.id).run();
          diag.feedback_update_res = updateRes;

          await db.prepare(`
            INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, signature)
            VALUES (datetime('now'), 'telegram:founder', 'owner', 'TELEGRAM_FEEDBACK_SAVED', ?, ?, 'sig_feedback')
          `).bind(`approval:${pending.id}`, JSON.stringify({ feedback: text, fromId, chatId })).run();

          await sendTelegramMessage(botToken, chatId, `✍️ **Consigne de modification enregistrée avec succès en base D1 !**\n\n> *"${text}"*\n\nL'agent adapte immédiatement le contenu.`);

          return new Response(JSON.stringify({ success: true, action: "FEEDBACK_SAVED", diag }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
          });
        }
      }
    }

    return new Response(JSON.stringify({ success: true, action: "IGNORED_UNRECOGNIZED", diag }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    console.error("Telegram Webhook Error:", err);
    return new Response(JSON.stringify({ error: err.message, stack: err.stack, diag }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
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

async function sendTelegramMessage(botToken, chatId, text) {
  if (!botToken || !chatId) return;
  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  try {
    await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: text
      })
    });
  } catch (e) {
    console.error("sendTelegramMessage error:", e);
  }
}
