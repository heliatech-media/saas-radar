/**
 * Cloudflare Pages Function: /api/subscribe
 * Captures email leads, dispatches instant Telegram alert to the executive desk,
 * and sends an executive welcome email via Resend (from briefing@heliatech.online).
 */

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

export async function onRequestGet() {
  return new Response(JSON.stringify({ status: "active", service: "heliatech-newsletter-api" }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
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
    const resendApiKey = context.env?.RESEND_API_KEY;

    // 1. Instant Telegram Alert to Executive Desk
    const telegramText = 
      `⭐ NOUVEAU SUBSCRIBER B2B HELIATECH !\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📧 Email : ${email}\n` +
      `🌍 Pays : ${country}\n` +
      `📄 Page : ${path}\n` +
      `🔗 Referrer : ${referrer}\n` +
      `⏰ Horodatage : ${now}\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━`;

    try {
      context.waitUntil(
        fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chat_id: chatId, text: telegramText }),
        })
      );
    } catch (telegramErr) {
      console.error("Telegram dispatch error:", telegramErr);
    }

    // 2. High-Converting Welcome Email via Resend
    if (resendApiKey) {
      const emailHtml = `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0b0f19; color: #f8fafc; padding: 40px 20px; max-width: 600px; margin: 0 auto; border-radius: 16px; border: 1px solid #1e293b;">
        <div style="text-align: center; margin-bottom: 30px;">
          <div style="display: inline-block; padding: 6px 14px; border-radius: 9999px; background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.3); color: #22d3ee; font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;">
            ⚡ HELIATECH CONFIDENTIAL
          </div>
          <h1 style="color: #ffffff; font-size: 24px; font-weight: 900; margin-top: 16px; margin-bottom: 8px; letter-spacing: -0.02em;">
            Access Granted: Your Executive SaaS Intelligence
          </h1>
          <p style="color: #94a3b8; font-size: 14px; margin: 0;">
            Welcome to the private briefing circle for modern CTOs, founders, and Ops leaders.
          </p>
        </div>

        <div style="background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 24px; margin-bottom: 24px;">
          <h3 style="color: #38bdf8; font-size: 15px; margin-top: 0; margin-bottom: 12px;">
            🎯 Here are your 3 priority executive resources:
          </h3>
          <ul style="color: #cbd5e1; font-size: 13px; line-height: 1.8; padding-left: 20px; margin: 0;">
            <li>
              <strong><a href="https://heliatech.online/calculator/" style="color: #22d3ee; text-decoration: none;">Interactive SaaS ROI & Break-Even Calculator ➔</a></strong><br/>
              Simulate operational costs, team time savings, and annual ROI across 50+ enterprise architectures.
            </li>
            <li style="margin-top: 10px;">
              <strong><a href="https://heliatech.online/tools/" style="color: #22d3ee; text-decoration: none;">The 2026 Developer & Automation Stack Index ➔</a></strong><br/>
              Uncompromising, zero-fluff code and performance audits (Make, Resend, Supabase, Vercel).
            </li>
            <li style="margin-top: 10px;">
              <strong><a href="https://heliatech.online/deals/" style="color: #22d3ee; text-decoration: none;">Exclusive Enterprise Stack Discounts & Credits ➔</a></strong><br/>
              Verified partner credits and extended trials negotiated directly for HeliaTech subscribers.
            </li>
          </ul>
        </div>

        <p style="color: #94a3b8; font-size: 13px; line-height: 1.6; margin-bottom: 24px;">
          Every Thursday at 9:00 AM EST, expect a razor-sharp breakdown of infrastructure shifts, hidden pricing traps, and emerging tooling before they hit mainstream tech circles.
        </p>

        <div style="text-align: center; border-top: 1px solid #1e293b; padding-top: 20px; font-size: 11px; color: #64748b;">
          <p style="margin: 0;">HeliaTech Research Division &copy; 2026 • San Francisco • Paris</p>
          <p style="margin: 4px 0 0;">Zero Spam Guarantee • If you ever wish to opt out, you can unsubscribe in one click.</p>
        </div>
      </div>
      `;

      try {
        context.waitUntil(
          fetch("https://api.resend.com/emails", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${resendApiKey}`,
              "Content-Type": "application/json",
              "User-Agent": "HeliaTech-Worker/1.0"
            },
            body: JSON.stringify({
              from: "HeliaTech <partnership@heliatech.online>",
              to: [email],
              subject: "⚡ [HELIATECH] Your Executive SaaS Briefing & ROI Intelligence Access",
              html: emailHtml
            })
          })
        );
      } catch (resendErr) {
        console.error("Resend dispatch error:", resendErr);
      }
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
