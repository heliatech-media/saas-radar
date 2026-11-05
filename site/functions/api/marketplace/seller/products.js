/**
 * Cloudflare Pages Edge Function: /api/marketplace/seller/products
 * Seller products catalog management & Sentinel AST upload security validator
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
    const products = [
      {
        id: "prod_001",
        slug: "n8n-ai-lead-enricher-waterfall",
        title: "n8n AI Waterfall Lead Enrichment & Scoring Engine",
        ecosystem: "n8n",
        category: "Lead Gen & Sales",
        price_usd: 49.00,
        status: "PUBLISHED",
        version: "v1.4.2",
        sales_count: 142,
        gross_revenue_usd: 6958.00,
        net_revenue_usd: 5566.40,
        rating: 4.95,
        reviews_count: 28,
        sentinel_scan_status: "CLEAN",
        last_updated: "2026-10-15"
      },
      {
        id: "prod_002",
        slug: "n8n-stripe-mrr-telegram-executive-radar",
        title: "n8n Stripe MRR & Cashflow Realtime Executive Telegram Radar",
        ecosystem: "n8n",
        category: "Fintech & RevOps",
        price_usd: 0.00,
        is_free: true,
        status: "PUBLISHED",
        version: "v1.2.0",
        sales_count: 410,
        gross_revenue_usd: 0.00,
        net_revenue_usd: 0.00,
        rating: 4.95,
        reviews_count: 31,
        sentinel_scan_status: "CLEAN",
        last_updated: "2026-10-10"
      },
      {
        id: "prod_003",
        slug: "n8n-salesforce-enterprise-bi-sync",
        title: "n8n Salesforce & Snowflake Enterprise BI Warehouse Pipeline",
        ecosystem: "n8n",
        category: "CRM & Sales",
        price_usd: 89.00,
        status: "PENDING_REVIEW",
        version: "v1.0.0",
        sales_count: 0,
        gross_revenue_usd: 0.00,
        net_revenue_usd: 0.00,
        rating: 0.0,
        reviews_count: 0,
        sentinel_scan_status: "CLEAN",
        last_updated: "2026-11-04"
      }
    ];

    return new Response(JSON.stringify({
      success: true,
      total_products: products.length,
      products
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch seller products"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json().catch(() => ({}));
    const { title, ecosystem, category, price_usd, workflow_json, submit_for_review } = body;

    if (!title || !ecosystem || !category) {
      return new Response(JSON.stringify({ success: false, error: "Missing required fields (title, ecosystem, category)" }), { status: 400 });
    }

    // Run Sentinel AST Security Scanner on uploaded code
    let scanResult = { clean: true, score: 100, warnings: [] };
    if (workflow_json) {
      const jsonStr = typeof workflow_json === 'string' ? workflow_json : JSON.stringify(workflow_json);
      
      // Check for hardcoded API keys or external suspicious webhook exfiltrations
      const leakedKeyPatterns = [
        /sk-[a-zA-Z0-9]{32,}/,
        /ghp_[a-zA-Z0-9]{36}/,
        /xox[baprs]-[0-9a-zA-Z]{10,}/,
        /AIza[0-9A-Za-z-_]{35}/
      ];

      for (const pattern of leakedKeyPatterns) {
        if (pattern.test(jsonStr)) {
          scanResult.clean = false;
          scanResult.score = 0;
          scanResult.warnings.push("Clé secrète d'API détectée en dur dans le fichier. Veuillez utiliser les variables d'environnement.");
          break;
        }
      }

      if (jsonStr.includes("webhook.site") || jsonStr.includes("pipedream.net") || jsonStr.includes("requestbin")) {
        scanResult.clean = false;
        scanResult.score = 20;
        scanResult.warnings.push("URL de capture externe suspecte détectée (webhook.site / pipedream).");
      }
    }

    if (!scanResult.clean) {
      return new Response(JSON.stringify({
        success: false,
        error: "Échec de l'audit de sécurité Sentinel Anti-Scam",
        scan_report: scanResult
      }), { status: 422 });
    }

    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    const priceNum = parseFloat(price_usd) || 0;

    const newProduct = {
      id: `prod_${Date.now()}`,
      slug,
      title: title.trim(),
      ecosystem: ecosystem.toLowerCase(),
      category: category.trim(),
      price_usd: priceNum,
      is_free: priceNum === 0,
      status: submit_for_review ? "PENDING_REVIEW" : "DRAFT",
      version: "v1.0.0",
      sales_count: 0,
      gross_revenue_usd: 0.00,
      net_revenue_usd: 0.00,
      rating: 5.0,
      reviews_count: 0,
      sentinel_scan_status: "CLEAN",
      sentinel_score: scanResult.score,
      created_at: new Date().toISOString()
    };

    return new Response(JSON.stringify({
      success: true,
      message: submit_for_review 
        ? "Produit certifié Sentinel 100/100 et soumis pour validation administrative !"
        : "Brouillon sauvegardé avec succès !",
      product: newProduct
    }), {
      status: 201,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to create product"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
