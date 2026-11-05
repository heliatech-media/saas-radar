/**
 * Cloudflare Pages Edge Function: /api/marketplace/seller/overview
 * Seller Studio analytics, 80% net revenue split, and payout balances
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
    const overview = {
      store_name: "AutomateScale Studio",
      badge: "Verified Pro Agency",
      currency: "USD",
      payout_split_percent: 80,
      platform_cut_percent: 20,
      total_gross_revenue: 6958.00,
      total_net_revenue: 5566.40, // 80%
      monthly_gross_revenue: 1840.00,
      monthly_net_revenue: 1472.00, // 80%
      available_payout_balance: 1472.00,
      pending_payout_balance: 320.00,
      total_sales_count: 142,
      average_rating: 4.95,
      conversion_rate_percent: 4.8,
      sales_chart: [
        { period: "Semaine 1", sales: 18, net_usd: 705.60 },
        { period: "Semaine 2", sales: 24, net_usd: 940.80 },
        { period: "Semaine 3", sales: 31, net_usd: 1215.20 },
        { period: "Semaine 4", sales: 42, net_usd: 1646.40 }
      ],
      recent_sales: [
        {
          id: "sale_8812",
          product_title: "n8n AI Waterfall Lead Enrichment & Scoring Engine",
          date: "18 Octobre 2026",
          gross_usd: 49.00,
          platform_cut_usd: 9.80, // 20%
          net_payout_usd: 39.20, // 80%
          buyer_email_masked: "al***@heliatech.online",
          status: "PAID"
        },
        {
          id: "sale_8810",
          product_title: "n8n AI Waterfall Lead Enrichment & Scoring Engine",
          date: "17 Octobre 2026",
          gross_usd: 49.00,
          platform_cut_usd: 9.80,
          net_payout_usd: 39.20,
          buyer_email_masked: "ma***@saasgrowth.io",
          status: "PAID"
        },
        {
          id: "sale_8805",
          product_title: "n8n AI Waterfall Lead Enrichment & Scoring Engine",
          date: "16 Octobre 2026",
          gross_usd: 49.00,
          platform_cut_usd: 9.80,
          net_payout_usd: 39.20,
          buyer_email_masked: "sa***@cloudscale.co",
          status: "PAID"
        }
      ],
      alerts: [
        {
          type: "INFO",
          message: "Compte Stripe Connect / SEPA vérifié et prêt pour les versements automatiques."
        },
        {
          type: "UPDATE_RECOMMENDED",
          message: "Le nœud Anthropic v1 a été mis à jour par n8n. Pensez à publier la version v1.5.0 de votre blueprint."
        }
      ]
    };

    return new Response(JSON.stringify({
      success: true,
      overview
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch seller overview"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
