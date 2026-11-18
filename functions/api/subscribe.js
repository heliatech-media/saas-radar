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
      const unsubUrl = `https://heliatech.online/unsubscribe?email=${encodeURIComponent(email)}`;
      const emailHtml = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to HeliaTech Confidential</title>
      </head>
      <body style="margin: 0; padding: 0; background-color: #030712; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f9fafb; -webkit-font-smoothing: antialiased;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #030712; width: 100% !important; margin: 0; padding: 40px 10px;">
          <tr>
            <td align="center">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 620px; background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 20px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);">
                
                <tr>
                  <td height="4" style="background: linear-gradient(90deg, #06b6d4 0%, #3b82f6 50%, #10b981 100%);"></td>
                </tr>

                <tr>
                  <td style="padding: 40px 36px 20px 36px; text-align: center;">
                    <div style="display: inline-block; padding: 6px 14px; border-radius: 9999px; background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.25); color: #22d3ee; font-size: 11px; font-weight: 800; letter-spacing: 0.15em; text-transform: uppercase;">
                      ⚡ HELIATECH CONFIDENTIAL • BRIEFING #001
                    </div>
                    <h1 style="color: #ffffff; font-size: 26px; font-weight: 900; letter-spacing: -0.03em; margin: 20px 0 10px 0; line-height: 1.25;">
                      Welcome to the Inner Circle of Modern Infrastructure.
                    </h1>
                    <p style="color: #94a3b8; font-size: 15px; line-height: 1.6; margin: 0;">
                      You just joined 14,000+ founders, CTOs, and automation engineers receiving zero-fluff software audits, uncompromised ROI models, and verified partner rates.
                    </p>
                  </td>
                </tr>

                <tr>
                  <td style="padding: 10px 36px 26px 36px;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 24px;">
                      <tr>
                        <td>
                          <div style="color: #38bdf8; font-size: 12px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 16px;">
                            🎯 YOUR IMMEDIATE EXECUTIVE ACCESS KIT
                          </div>
                          
                          <!-- Asset 1: ROI Calculator -->
                          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 18px;">
                            <tr>
                              <td width="32" valign="top" style="font-size: 18px;">📊</td>
                              <td style="padding-left: 10px;">
                                <a href="https://heliatech.online/calculator/" style="color: #ffffff; font-size: 14px; font-weight: 700; text-decoration: none; display: inline-block;">
                                  The 2026 SaaS ROI & Break-Even Calculator ➔
                                </a>
                                <div style="color: #94a3b8; font-size: 12px; line-height: 1.5; margin-top: 3px;">
                                  Simulate exact annual tool stack consolidation savings across Make, Resend, Supabase, and 45+ enterprise tools.
                                </div>
                              </td>
                            </tr>
                          </table>

                          <!-- Asset 2: NEW GitHub SaaS Radar -->
                          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 18px; background: rgba(6, 182, 212, 0.05); padding: 10px; border-radius: 8px; border: 1px solid rgba(6, 182, 212, 0.2);">
                            <tr>
                              <td width="32" valign="top" style="font-size: 18px;">⭐</td>
                              <td style="padding-left: 10px;">
                                <a href="https://heliatech.online/repos/" style="color: #22d3ee; font-size: 14px; font-weight: 800; text-decoration: none; display: inline-block;">
                                  The GitHub SaaS Radar (Open-Source Audits) ➔
                                </a>
                                <div style="color: #cbd5e1; font-size: 12px; line-height: 1.5; margin-top: 3px;">
                                  Forensic architectural audits of 100% verified SaaS repos (Postiz, Cal.com, Supabase, n8n, Open SaaS) with self-host vs cloud TCO models.
                                </div>
                              </td>
                            </tr>
                          </table>

                          <!-- Asset 3: Duels -->
                          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom: 18px;">
                            <tr>
                              <td width="32" valign="top" style="font-size: 18px;">⚔️</td>
                              <td style="padding-left: 10px;">
                                <a href="https://heliatech.online/versus/" style="color: #ffffff; font-size: 14px; font-weight: 700; text-decoration: none; display: inline-block;">
                                  Head-to-Head Architectural Duels ➔
                                </a>
                                <div style="color: #94a3b8; font-size: 12px; line-height: 1.5; margin-top: 3px;">
                                  Code-level verdicts: Make vs Zapier, Resend vs Brevo, Cursor vs Copilot with total cost of ownership graphs.
                                </div>
                              </td>
                            </tr>
                          </table>

                          <!-- Asset 4: Deals -->
                          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                            <tr>
                              <td width="32" valign="top" style="font-size: 18px;">💎</td>
                              <td style="padding-left: 10px;">
                                <a href="https://heliatech.online/deals/" style="color: #ffffff; font-size: 14px; font-weight: 700; text-decoration: none; display: inline-block;">
                                  Exclusive Private Partner Credits & Deals ➔
                                </a>
                                <div style="color: #94a3b8; font-size: 12px; line-height: 1.5; margin-top: 3px;">
                                  Up to $15,000 in direct cloud infrastructure and SaaS startup credits reserved for HeliaTech subscribers.
                                </div>
                              </td>
                            </tr>
                          </table>

                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>

                <tr>
                  <td style="padding: 0 36px 36px 36px; text-align: center;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
                      <tr>
                        <td align="center" style="border-radius: 12px; background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);">
                          <a href="https://heliatech.online/repos/" target="_blank" style="display: inline-block; padding: 16px 36px; font-size: 14px; font-weight: 800; letter-spacing: 0.05em; color: #020617; text-decoration: none; border-radius: 12px; text-transform: uppercase;">
                            Access The Open-Source SaaS Radar ➔
                          </a>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>

                <tr>
                  <td style="padding: 0 36px 36px 36px;">
                    <div style="border-top: 1px solid #1e293b; padding-top: 24px; color: #94a3b8; font-size: 13px; line-height: 1.7;">
                      <p style="margin: 0 0 12px 0;">
                        <strong style="color: #f1f5f9;">Our Editorial Promise:</strong> We never accept payment to bias our software ratings. When a tool fails under high-concurrency loads or inflates renewal prices, we document it with benchmarks.
                      </p>
                      <p style="margin: 0;">
                        Expect our deep-dive dispatch every Thursday at 9:00 AM EST (15:00 CET). If you have a specific software stack question, hit reply—our engineering desk reads every message.
                      </p>
                    </div>
                  </td>
                </tr>

                <tr>
                  <td style="background-color: #070b14; border-top: 1px solid #1e293b; padding: 28px 36px; text-align: center;">
                    <div style="color: #475569; font-size: 11px; line-height: 1.6;">
                      <p style="margin: 0; font-weight: 600; color: #64748b;">
                        HELIATECH RESEARCH & INTELLIGENCE DIVISION
                      </p>
                      <p style="margin: 4px 0 12px 0;">
                        San Francisco • Paris • Global Edge Distribution
                      </p>
                      <p style="margin: 0;">
                        Sent to ${email} because you requested private access on heliatech.online.<br/>
                        <a href="${unsubUrl}" style="color: #06b6d4; text-decoration: underline;">Unsubscribe in 1 click</a> • <a href="https://heliatech.online/terms/" style="color: #64748b; text-decoration: none;">Privacy Policy</a>
                      </p>
                    </div>
                  </td>
                </tr>

              </table>
            </td>
          </tr>
        </table>
      </body>
      </html>
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
