/**
 * Cloudflare Pages Edge Function: /api/telemetry
 * High-performance edge endpoint for real-time telemetry caching & conversion beacon ingestion.
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

export async function onRequestPost(context) {
  try {
    let body = {};
    try {
      body = await context.request.json();
    } catch (e) {
      // Beacon may send text/plain
      const text = await context.request.text();
      body = JSON.parse(text || "{}");
    }

    const type = body.type || "VISIT";
    const country = context.request.headers.get("cf-ipcountry") || "Unknown";
    const tool = body.tool || body.title || "Unknown Tool";
    const path = body.path || "/";
    const referrer = body.referrer || "Direct / Organic";
    const now = new Date().toLocaleTimeString("en-US", { hour12: false });

    const botToken = context.env?.TELEGRAM_BOT_TOKEN || "8897785268:AAG12hNOLn9x3bFJI_qzSad-sGF8wUY_HD4";
    const chatId = context.env?.TELEGRAM_CHAT_ID || "8819768123";

    // Immediate Alert on High-Value Commercial Events (Affiliate Hop)
    if (type === "HOP" || type === "CONVERSION") {
      const msg = 
        `🎯 [HELIATECH CONVERSION - AFFILIATE HOP]\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `🚀 Outil Cliqué : ${tool.toUpperCase()}\n` +
        `🌍 Pays Visiteur : ${country}\n` +
        `📄 Page Source : ${path}\n` +
        `🔗 Referrer : ${referrer}\n` +
        `⏰ Horodatage : ${now} UTC\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━`;

      try {
        context.waitUntil(
          fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chat_id: chatId, text: msg }),
          })
        );
      } catch (err) {
        console.error("Telegram beacon dispatch error:", err);
      }
    }

    return new Response(JSON.stringify({ ok: true, type: type, timestamp: now }), {
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

export async function onRequestGet(context) {
  const cacheKey = new Request("https://heliatech.online/api/telemetry", context.request);
  const cache = caches.default;
  let response = await cache.match(cacheKey);

  if (!response) {
    try {
      const res = await fetch("https://heliatech.online/data/live_cloudflare_telemetry.json?t=" + Date.now(), {
        headers: { "User-Agent": "HeliaTech-Edge-Worker/1.0" }
      });
      if (res.ok) {
        const data = await res.json();
        response = new Response(JSON.stringify(data), {
          headers: {
            "Content-Type": "application/json",
            "Cache-Control": "public, max-age=30, s-maxage=30",
            "Access-Control-Allow-Origin": "*",
            "X-Edge-Origin": "Cloudflare-Pages-Function"
          }
        });
        context.waitUntil(cache.put(cacheKey, response.clone()));
        return response;
      }
    } catch (e) {
      // Fallback
    }
    
    // Fallback response
    response = new Response(JSON.stringify({
      status: "EDGE_ACTIVE",
      total_visitors_network: 3616,
      total_requests: 34147,
      total_visits: 1120,
      total_pageviews: 7051
    }), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }

  return response;
}
