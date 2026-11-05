/**
 * Cloudflare Pages Edge Function: /api/marketplace/admin/sellers
 * Seller onboarding applications review & custom commission rate override
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
    const pendingApplications = [
      {
        id: "app_pending_101",
        applicant_name: "Julien M.",
        email: "julien.revops@paristech.io",
        store_name: "ParisRevOps Engineering",
        bio: "Expert certifié Make et n8n avec 6 ans d'expérience en architecture CRM HubSpot & Salesforce.",
        portfolio_url: "https://parisrevops.example.com",
        specialties: ["n8n", "Make", "HubSpot", "PostgreSQL"],
        submitted_at: "2026-11-04T16:20:00Z",
        status: "PENDING"
      }
    ];

    const activeSellers = [
      {
        id: "seller_001",
        name: "AutomateScale Studio",
        slug: "automatescale-studio",
        email: "automatescale@heliatech.online",
        commission_rate_percent: 20,
        seller_payout_percent: 80,
        total_sales: 142,
        gross_volume_usd: 6958.00,
        status: "ACTIVE"
      },
      {
        id: "seller_002",
        name: "CloudFlow Ops",
        slug: "cloudflow-ops",
        email: "cloudflow@example.com",
        commission_rate_percent: 20,
        seller_payout_percent: 80,
        total_sales: 540,
        gross_volume_usd: 0.00, // free templates
        status: "ACTIVE"
      }
    ];

    return new Response(JSON.stringify({
      success: true,
      pending_applications: pendingApplications,
      active_sellers: activeSellers
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch sellers data"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json().catch(() => ({}));
    const { application_id, action, reason, custom_commission_rate } = body;

    if (!application_id || !action) {
      return new Response(JSON.stringify({ success: false, error: "Missing application_id or action" }), { status: 400 });
    }

    if (action === "approve") {
      return new Response(JSON.stringify({
        success: true,
        message: "Candidature approuvée ! Le compte utilisateur a été promu au rôle SELLER (80% net).",
        seller_status: "ACTIVE",
        commission_rate: custom_commission_rate || 20
      }), { status: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
    }

    if (action === "reject") {
      return new Response(JSON.stringify({
        success: true,
        message: `Candidature refusée. Motif notifié au candidat : ${reason || "Dossier incomplet"}`,
        seller_status: "REJECTED"
      }), { status: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
    }

    return new Response(JSON.stringify({ success: false, error: "Invalid action" }), { status: 400 });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to process seller application"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
