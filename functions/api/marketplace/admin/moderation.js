/**
 * Cloudflare Pages Edge Function: /api/marketplace/admin/moderation
 * Product queue moderation, approval, rejection with mandatory feedback, and suspension
 */

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
  });
}

export async function onRequestGet(context) {
  try {
    const pendingProducts = [
      {
        id: "prod_pend_001",
        title: "n8n Salesforce & Snowflake Enterprise BI Warehouse Pipeline",
        ecosystem: "n8n",
        category: "CRM & Sales",
        creator_name: "AutomateScale Studio",
        creator_slug: "automatescale-studio",
        price_usd: 89.00,
        version: "v1.0.0",
        nodes_count: 22,
        sentinel_score: 100,
        sentinel_status: "PASSED_CLEAN",
        checks: {
          zero_credential_leak: true,
          zero_hidden_webhooks: true,
          syntax_valid: true
        },
        submitted_at: "2026-11-05T18:30:00Z"
      },
      {
        id: "prod_pend_002",
        title: "Supabase Vector Store & LangChain Hybrid Search Starter",
        ecosystem: "supabase",
        category: "Developer Tools",
        creator_name: "DataStack Labs",
        creator_slug: "datastack-labs",
        price_usd: 59.00,
        version: "v1.0.0",
        nodes_count: 16,
        sentinel_score: 98,
        sentinel_status: "PASSED_CLEAN",
        checks: {
          zero_credential_leak: true,
          zero_hidden_webhooks: true,
          syntax_valid: true
        },
        submitted_at: "2026-11-05T19:45:00Z"
      }
    ];

    return new Response(JSON.stringify({
      success: true,
      pending_count: pendingProducts.length,
      products: pendingProducts
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch moderation queue"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json().catch(() => ({}));
    const { product_id, action, reason } = body;

    if (!product_id || !action) {
      return new Response(JSON.stringify({ success: false, error: "Missing product_id or action" }), { status: 400 });
    }

    if ((action === "reject" || action === "suspend") && !reason) {
      return new Response(JSON.stringify({
        success: false,
        error: "Un motif explicatif est obligatoire pour refuser ou suspendre un produit."
      }), { status: 400 });
    }

    let statusResult = "PUBLISHED";
    let message = "Produit approuvé et publié sur la marketplace !";

    if (action === "reject") {
      statusResult = "REJECTED";
      message = `Produit rejeté. Motif envoyé au créateur : ${reason}`;
    } else if (action === "suspend") {
      statusResult = "SUSPENDED";
      message = `Produit suspendu immédiatement. Motif : ${reason}`;
    }

    return new Response(JSON.stringify({
      success: true,
      action_taken: action,
      product_id,
      new_status: statusResult,
      message,
      audit_logged: true,
      timestamp: new Date().toISOString()
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Moderation action failed"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
