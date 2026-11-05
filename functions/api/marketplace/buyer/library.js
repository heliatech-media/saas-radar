/**
 * Cloudflare Pages Edge Function: /api/marketplace/buyer/library
 * Buyer's digital entitlements, active licenses, versions, and update statuses
 */
import { PRODUCTS } from "../_catalog.js";

function base64UrlDecode(str) {
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) str += '=';
  return atob(str);
}

async function verifyJwt(token, secret) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const [headerB64, payloadB64, signatureB64] = parts;
    const dataToVerify = `${headerB64}.${payloadB64}`;
    const enc = new TextEncoder();

    const key = await crypto.subtle.importKey(
      'raw',
      enc.encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify']
    );

    const binarySignature = atob(signatureB64.replace(/-/g, '+').replace(/_/g, '/'));
    const sigBytes = new Uint8Array(binarySignature.length);
    for (let i = 0; i < binarySignature.length; i++) {
      sigBytes[i] = binarySignature.charCodeAt(i);
    }

    const isValid = await crypto.subtle.verify('HMAC', key, sigBytes, enc.encode(dataToVerify));
    if (!isValid) return null;

    const payload = JSON.parse(base64UrlDecode(payloadB64));
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) return null;

    return payload;
  } catch (e) {
    return null;
  }
}

function getAuthUser(context) {
  const jwtSecret = context.env?.MARKETPLACE_JWT_SECRET || "heliatech_secret_hmac_key_2026_super_secure";
  let token = null;

  const authHeader = context.request.headers.get("Authorization");
  if (authHeader && authHeader.startsWith("Bearer ")) {
    token = authHeader.substring(7);
  }

  if (!token) {
    const cookieHeader = context.request.headers.get("Cookie");
    if (cookieHeader) {
      const match = cookieHeader.match(/ht_session=([^;]+)/);
      if (match) token = match[1];
    }
  }

  if (!token) return null;
  return verifyJwt(token, jwtSecret);
}

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
    const user = await getAuthUser(context);

    // Default buyer entitlements catalog items
    const defaultBlueprints = [
      {
        id: "pur_default_001",
        product_id: "tpl_n8n_ai_lead_enricher",
        product_slug: "n8n-ai-lead-enricher-waterfall",
        title: "n8n AI Waterfall Lead Enrichment & Scoring Engine",
        ecosystem: "n8n",
        category: "Lead Gen & Sales",
        price_usd: 49,
        license_key: "HLT-LIC-N8N-8842-PRO-2026",
        purchased_at: "2026-10-18T14:32:00Z",
        version_purchased: "v1.2.0",
        latest_version: "v1.4.2",
        has_update: true,
        download_count: 3,
        creator: {
          name: "AutomateScale Studio",
          slug: "automatescale-studio",
          avatar: "https://api.dicebear.com/7.x/identicon/svg?seed=AutomateScale"
        }
      },
      {
        id: "pur_default_002",
        product_id: "tpl_make_stripe_churn_rescue",
        product_slug: "make-stripe-churn-rescue-blueprint",
        title: "Make.com Stripe Failed Payment Recovery & Smart Churn Rescue",
        ecosystem: "make",
        category: "Fintech & RevOps",
        price_usd: 39,
        license_key: "HLT-LIC-MAK-9102-PRO-2026",
        purchased_at: "2026-10-25T09:15:00Z",
        version_purchased: "v1.1.0",
        latest_version: "v1.1.0",
        has_update: false,
        download_count: 1,
        creator: {
          name: "SaaSGrowth Ops",
          slug: "saasgrowth-ops",
          avatar: "https://api.dicebear.com/7.x/identicon/svg?seed=SaaSGrowth"
        }
      }
    ];

    return new Response(JSON.stringify({
      success: true,
      user_id: user?.sub || "demo_buyer_user",
      is_authenticated: Boolean(user),
      total_items: defaultBlueprints.length,
      library: defaultBlueprints
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
      error: error.message || "Failed to fetch buyer library"
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}

export async function onRequestPost(context) {
  try {
    const user = await getAuthUser(context);
    const body = await context.request.json().catch(() => ({}));
    const slug = body.product_slug;

    if (!slug) {
      return new Response(JSON.stringify({ success: false, error: "Missing product_slug" }), { status: 400 });
    }

    const target = PRODUCTS.find(p => p.slug === slug);
    if (!target) {
      return new Response(JSON.stringify({ success: false, error: "Product not found" }), { status: 404 });
    }

    // Only allow free direct addition if unpaid
    if (!target.is_free && target.price_usd > 0 && !body.is_mock_purchase) {
      return new Response(JSON.stringify({ success: false, error: "This product requires checkout" }), { status: 402 });
    }

    const randomSuffix = Math.random().toString(36).substring(2, 6).toUpperCase();
    const newPurchase = {
      id: `pur_${Date.now()}`,
      product_id: target.id,
      product_slug: target.slug,
      title: target.title,
      ecosystem: target.ecosystem,
      category: target.category,
      price_usd: target.price_usd,
      license_key: `HLT-LIC-${target.ecosystem.substring(0, 3).toUpperCase()}-${randomSuffix}-2026`,
      purchased_at: new Date().toISOString(),
      version_purchased: target.version || "v1.0.0",
      latest_version: target.version || "v1.0.0",
      has_update: false,
      download_count: 0,
      creator: {
        name: target.creator?.name || "Verified Creator",
        slug: target.creator?.slug || "creator",
        avatar: target.creator?.avatar || ""
      }
    };

    return new Response(JSON.stringify({
      success: true,
      message: "Template successfully added to library!",
      purchase: newPurchase
    }), {
      status: 201,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to add product to library"
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}
