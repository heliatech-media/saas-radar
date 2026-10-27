/**
 * Cloudflare Pages Edge Function: /api/telemetry
 * High-performance edge endpoint for real-time telemetry caching & delivery.
 */
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
      total_visitors_network: 2368,
      total_requests: 24010,
      total_visits: 734,
      total_pageviews: 5098
    }), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }

  return response;
}
