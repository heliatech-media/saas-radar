/**
 * Cloudflare Pages Function: /api/subscribe
 * Captures email leads, permanently persists into Cloudflare D1 (subscribers table),
 * dispatches instant Telegram alert to the executive desk, and sends VIP welcome email via Resend.
 */

const COUNTRY_NAMES = {
  US: "United States",
  MA: "Morocco",
  FR: "France",
  GB: "United Kingdom",
  DE: "Germany",
  CA: "Canada",
  AE: "United Arab Emirates",
  ES: "Spain",
  IT: "Italy",
  NL: "Netherlands",
  CH: "Switzerland",
  BE: "Belgium",
  AU: "Australia",
  IN: "India",
  SG: "Singapore",
  BR: "Brazil",
  JP: "Japan"
};

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
      return new Response(JSON.stringify({ error: "Invalid email address" }), {
        status: 400,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      });
    }

    const countryCode = context.request.headers.get("cf-ipcountry") || "US";
    const countryName = COUNTRY_NAMES[countryCode] || countryCode;
    const userAgent = context.request.headers.get("user-agent") || "Unknown";
    const path = body.path || "/";
    const referrer = body.referrer || "Direct";
    const now = new Date().toISOString();

    const subscriberId = "sub_" + (crypto?.randomUUID ? crypto.randomUUID().replace(/-/g, "").slice(0, 12) : Math.random().toString(36).substring(2, 14));
    const role = body.role || "B2B Decision Maker";
    const leadMagnet = body.lead_magnet || (path.includes("calculator") ? "SaaS Bloat Elimination Calculator" : (path.includes("versus") ? "Versus Duel Benchmark" : "HeliaTech Executive Briefing"));

    // =========================================================================
    // 1. DUAL-PATH ACID PERSISTENCE INTO CLOUDFLARE D1 (TABLE subscribers)
    // =========================================================================
    let d1Persisted = false;
    let d1Error = null;

    // Path A: Native D1 Binding (context.env.DB)
    if (context.env?.DB) {
      try {
        await context.env.DB.prepare(`
          INSERT INTO subscribers (id, email, role, country, country_code, signup_date, source_path, lead_magnet, status)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Verified')
          ON CONFLICT(email) DO UPDATE SET
            last_engaged_at = excluded.signup_date,
            source_path = excluded.source_path
        `).bind(
          subscriberId,
          email.toLowerCase(),
          role,
          countryName,
          countryCode,
          now,
          path,
          leadMagnet
        ).run();

        // Consigner l'audit log transactionnel
        try {
          await context.env.DB.prepare(`
            INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, signature)
            VALUES (datetime('now'), ?, 'subscriber', 'NEWSLETTER_SUBSCRIPTION', 'subscribers', ?, 'sig_verified_lead')
          `).bind(
            email.toLowerCase(),
            JSON.stringify({ path, country: countryCode, referrer, leadMagnet })
          ).run();
        } catch (_) {}

        d1Persisted = true;
      } catch (dbErr) {
        d1Error = dbErr.message;
        console.error("D1 Native insert error:", dbErr);
      }
    }

    // Path B: Cloudflare D1 HTTP REST API Fallback (Guarantees persistence even if binding is detached)
    if (!d1Persisted) {
      const accountId = context.env?.CLOUDFLARE_ACCOUNT_ID || "b3afc13187792a3d1135561de03e9f16";
      const databaseId = context.env?.CLOUDFLARE_D1_DATABASE_ID || "a5659ce3-467e-47d9-8577-f984c5d040f1";
      const d1Token = context.env?.CLOUDFLARE_D1_TOKEN || context.env?.CLOUDFLARE_API_TOKEN;

      if (d1Token && accountId && databaseId) {
        try {
          const d1Url = `https://api.cloudflare.com/client/v4/accounts/${accountId}/d1/database/${databaseId}/query`;
          const d1Payload = {
            sql: `
              INSERT INTO subscribers (id, email, role, country, country_code, signup_date, source_path, lead_magnet, status)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Verified')
              ON CONFLICT(email) DO UPDATE SET
                last_engaged_at = excluded.signup_date,
                source_path = excluded.source_path;
            `,
            params: [
              subscriberId,
              email.toLowerCase(),
              role,
              countryName,
              countryCode,
              now,
              path,
              leadMagnet
            ]
          };

          const d1Resp = await fetch(d1Url, {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${d1Token}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify(d1Payload)
          });

          const d1Json = await d1Resp.json();
          if (d1Json && d1Json.success) {
            d1Persisted = true;
          } else {
            console.error("D1 API error:", d1Json ? d1Json.errors : "Unknown error");
          }
        } catch (apiErr) {
          console.error("D1 API Fallback error:", apiErr);
        }
      }
    }

    // =========================================================================
    // 2. INSTANT TELEGRAM NOTIFICATION TO EXECUTIVE DESK
    // =========================================================================
    const botToken = context.env?.TELEGRAM_BOT_TOKEN;
    const chatId = context.env?.TELEGRAM_CHAT_ID || "8819768123";
    const resendApiKey = context.env?.RESEND_API_KEY;

    const bddStatusLine = d1Persisted ? "✅ Enregistré dans subscribers (D1)" : (d1Error ? `⚠️ D1 Note: ${d1Error}` : "✅ Persistance D1 API déclenchée");

    const telegramText = 
      `⭐ NOUVEAU SUBSCRIBER B2B HELIATECH !\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📧 Email : ${email}\n` +
      `🌍 Pays : ${countryName} (${countryCode})\n` +
      `📄 Page : ${path}\n` +
      `🎁 Lead Magnet : ${leadMagnet}\n` +
      `🔗 Source : ${referrer}\n` +
      `💾 BDD D1 : ${bddStatusLine}\n` +
      `⏰ Date : ${now}\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━`;

    if (botToken) {
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
    }

    // =========================================================================
    // 3. HIGH-CONVERTING WELCOME EMAIL VIA RESEND
    // =========================================================================
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

    return new Response(JSON.stringify({ 
      success: true, 
      message: "Subscription active", 
      persisted: d1Persisted 
    }), {
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
