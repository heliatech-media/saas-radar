/**
 * Cloudflare Pages Edge Function: /api/marketplace/buyer/orders
 * Buyer orders, invoices, and payment receipts
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
    const defaultOrders = [
      {
        order_id: "HLT-ORD-2026-8812",
        order_number: "#8812",
        date: "2026-10-18T14:32:00Z",
        formatted_date: "18 Oct 2026",
        status: "COMPLETED",
        total_usd: 49.00,
        currency: "USD",
        payment_method: "Carte Bancaire •••• 4242",
        items: [
          {
            title: "n8n AI Waterfall Lead Enrichment & Scoring Engine",
            slug: "n8n-ai-lead-enricher-waterfall",
            price_usd: 49.00,
            license_key: "HLT-LIC-N8N-8842-PRO-2026"
          }
        ],
        invoice_pdf_available: true,
        vat_amount_usd: 0.00
      },
      {
        order_id: "HLT-ORD-2026-9105",
        order_number: "#9105",
        date: "2026-10-25T09:15:00Z",
        formatted_date: "25 Oct 2026",
        status: "COMPLETED",
        total_usd: 39.00,
        currency: "USD",
        payment_method: "Apple Pay / Carte •••• 9811",
        items: [
          {
            title: "Make.com Stripe Failed Payment Recovery & Smart Churn Rescue",
            slug: "make-stripe-churn-rescue-blueprint",
            price_usd: 39.00,
            license_key: "HLT-LIC-MAK-9102-PRO-2026"
          }
        ],
        invoice_pdf_available: true,
        vat_amount_usd: 0.00
      }
    ];

    return new Response(JSON.stringify({
      success: true,
      total_orders: defaultOrders.length,
      orders: defaultOrders
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
      error: error.message || "Failed to fetch orders"
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}
