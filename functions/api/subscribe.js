/**
 * Cloudflare Pages Function: /api/subscribe
 * Captures email leads and dispatches instant Telegram alerts to executive desk.
 */

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const email = (body.email || "").trim();

    if (!email || !email.includes("@")) {
      return new Response(JSON.stringify({ error: "Invalid email" }), {
        status: 400,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      });
    }

    const country = context.request.headers.get("cf-ipcountry") || "Unknown";
    const userAgent = context.request.headers.get("user-agent") || "Unknown";
    const path = body.path || "/";
    const referrer = body.referrer || "Direct";
    const now = new Date().toISOString();

    const botToken = context.env?.TELEGRAM_BOT_TOKEN || "8897785268:AAG12hNOLn9x3bFJI_qzSad-sGF8wUY_HD4";
    const chatId = context.env?.TELEGRAM_CHAT_ID || "8819768123";

    const text = 
      `⭐ NOUVEAU SUBSCRIBER B2B HELIATECH !\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📧 Email : ${email}\n` +
      `🌍 Pays : ${country}\n` +
      `📄 Page d'entrée : ${path}\n` +
      `🔗 Referrer : ${referrer}\n` +
      `⏰ Horodatage : ${now}\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━`;

    try {
      context.waitUntil(
        fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chat_id: chatId, text: text }),
        })
      );
    } catch (telegramErr) {
      console.error("Telegram dispatch error:", telegramErr);
    }

    return new Response(JSON.stringify({ success: true, message: "Subscription active" }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }
}
