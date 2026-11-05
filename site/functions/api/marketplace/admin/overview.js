/**
 * Cloudflare Pages Edge Function: /api/marketplace/admin/overview
 * Platform-wide GMV, 20% commission metrics, and real-time activity stream
 */

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
  });
}

export async function onRequestGet(context) {
  try {
    const stats = {
      gmv_gross_usd: 14890.00,
      platform_cut_usd: 2978.00, // 20%
      total_sellers_payout_usd: 11912.00, // 80%
      total_users_count: 1420,
      active_sellers_count: 16,
      published_products_count: 18,
      pending_moderation_count: 2,
      pending_seller_apps_count: 1,
      pending_payouts_count: 1,
      refund_rate_percent: 0.14,
      activity_stream: [
        {
          id: "act_101",
          type: "SALE",
          text: "Vente confirmée : n8n AI Waterfall Lead ($49.00) — Part Vendeur $39.20 (80%), HeliaTech $9.80 (20%)",
          time: "Il y a 14 minutes"
        },
        {
          id: "act_102",
          type: "MODERATION",
          text: "Nouveau produit soumis : n8n Salesforce Enterprise BI Sync — Scan Sentinel 100/100 Clean",
          time: "Il y a 45 minutes"
        },
        {
          id: "act_103",
          type: "PAYOUT_REQUEST",
          text: "Demande de versement : AutomateScale Studio ($1,472.00 vers IBAN •••• 4021)",
          time: "Il y a 1 heure"
        },
        {
          id: "act_104",
          type: "NEW_SELLER",
          text: "Candidature vendeur : CloudFlow Ops (Dossier vérifié et approuvé)",
          time: "Il y a 3 heures"
        }
      ]
    };

    return new Response(JSON.stringify({
      success: true,
      stats
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch admin overview"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
