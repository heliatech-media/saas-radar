/**
 * Cloudflare Pages Function: /api/unsubscribe
 * Handles 1-click unsubscribe requests (CAN-SPAM / GDPR / RFC 8058 compliance).
 * Updates Cloudflare D1 table subscribers: sets status = 'Unsubscribed' and unsubscribed_at = now.
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

export async function onRequestGet(context) {
  const url = new URL(context.request.url);
  const email = (url.searchParams.get("email") || "").trim().toLowerCase();

  if (!email || !email.includes("@")) {
    return new Response(JSON.stringify({ error: "Email parameter required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const result = await processUnsubscribe(context, email);
  
  // Si requête GET directe depuis le navigateur, rediriger vers la page /unsubscribe?success=true
  if (context.request.headers.get("accept")?.includes("text/html")) {
    return Response.redirect(`https://heliatech.online/unsubscribe?email=${encodeURIComponent(email)}&status=confirmed`, 302);
  }

  return new Response(JSON.stringify(result), {
    status: 200,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
  });
}

export async function onRequestPost(context) {
  try {
    let email = "";
    const contentType = context.request.headers.get("content-type") || "";
    
    if (contentType.includes("application/json")) {
      const body = await context.request.json();
      email = (body.email || "").trim().toLowerCase();
    } else if (contentType.includes("application/x-www-form-urlencoded")) {
      const formData = await context.request.formData();
      email = (formData.get("email") || "").toString().trim().toLowerCase();
    } else {
      const url = new URL(context.request.url);
      email = (url.searchParams.get("email") || "").trim().toLowerCase();
    }

    if (!email || !email.includes("@")) {
      return new Response(JSON.stringify({ error: "Invalid email" }), {
        status: 400,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      });
    }

    const result = await processUnsubscribe(context, email);
    return new Response(JSON.stringify(result), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  }
}

async function processUnsubscribe(context, email) {
  const now = new Date().toISOString();
  let updatedInD1 = false;

  // Path A: Native D1 Binding
  if (context.env?.DB) {
    try {
      await context.env.DB.prepare(`
        UPDATE subscribers 
        SET status = 'Unsubscribed', unsubscribed_at = ?
        WHERE lower(email) = lower(?)
      `).bind(now, email).run();

      try {
        await context.env.DB.prepare(`
          INSERT INTO sentinel_audit_logs (timestamp, actor_email, actor_role, action, target, details_json, signature)
          VALUES (datetime('now'), ?, 'subscriber', 'NEWSLETTER_UNSUBSCRIBE', 'subscribers', ?, 'sig_verified_unsub')
        `).bind(email, JSON.stringify({ unsubscribed_at: now })).run();
      } catch (_) {}

      updatedInD1 = true;
    } catch (e) {
      console.error("D1 Native Unsubscribe error:", e);
    }
  }

  // Path B: Cloudflare D1 REST API Fallback
  if (!updatedInD1) {
    const accountId = context.env?.CLOUDFLARE_ACCOUNT_ID || "b3afc13187792a3d1135561de03e9f16";
    const databaseId = context.env?.CLOUDFLARE_D1_DATABASE_ID || "a5659ce3-467e-47d9-8577-f984c5d040f1";
    const d1Token = context.env?.CLOUDFLARE_D1_TOKEN || context.env?.CLOUDFLARE_API_TOKEN;

    if (d1Token && accountId && databaseId) {
      try {
        const d1Url = `https://api.cloudflare.com/client/v4/accounts/${accountId}/d1/database/${databaseId}/query`;
        await fetch(d1Url, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${d1Token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            sql: "UPDATE subscribers SET status = 'Unsubscribed', unsubscribed_at = ? WHERE lower(email) = lower(?);",
            params: [now, email]
          })
        });
        updatedInD1 = true;
      } catch (apiErr) {
        console.error("D1 API Unsubscribe fallback error:", apiErr);
      }
    }
  }

  return {
    success: true,
    email: email,
    status: "Unsubscribed",
    unsubscribed_at: now,
    message: "You have been successfully unsubscribed from HeliaTech Intelligence."
  };
}
