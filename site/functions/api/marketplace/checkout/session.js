/**
 * Cloudflare Pages Edge Function: /api/marketplace/checkout/session
 * Initiates checkout session with dynamic coupon calculation and 80/20 revenue split
 */
import { PRODUCTS } from "../_catalog.js";

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
  });
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json().catch(() => ({}));
    const { slug, coupon_code } = body;

    if (!slug) {
      return new Response(JSON.stringify({ success: false, error: "Missing product slug" }), { status: 400 });
    }

    const target = PRODUCTS.find(p => p.slug === slug);
    if (!target) {
      return new Response(JSON.stringify({ success: false, error: "Blueprint not found" }), { status: 404 });
    }

    const grossCents = (target.price_usd || 0) * 100;
    let discountCents = 0;

    // Apply Coupon Code
    if (coupon_code) {
      const codeClean = coupon_code.toUpperCase().trim();
      if (codeClean === "LAUNCH20") {
        discountCents = Math.round((grossCents * 20) / 100);
      } else if (codeClean === "BLACKFRIDAY") {
        discountCents = Math.min(grossCents, 1500); // $15 off
      }
    }

    const finalCents = Math.max(0, grossCents - discountCents);
    const platformFeeCents = Math.round((finalCents * 20) / 100);
    const sellerNetCents = finalCents - platformFeeCents;

    const sessionId = `cs_live_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`;
    const checkoutUrl = `/checkout/success?session_id=${sessionId}&slug=${target.slug}&amount=${(finalCents / 100).toFixed(2)}`;

    return new Response(JSON.stringify({
      success: true,
      session: {
        session_id: sessionId,
        checkout_url: checkoutUrl,
        product_title: target.title,
        amount_usd: (finalCents / 100).toFixed(2),
        gross_usd: (grossCents / 100).toFixed(2),
        discount_usd: (discountCents / 100).toFixed(2),
        platform_cut_usd: (platformFeeCents / 100).toFixed(2),
        seller_net_usd: (sellerNetCents / 100).toFixed(2),
        currency: "USD"
      }
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to create checkout session"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
