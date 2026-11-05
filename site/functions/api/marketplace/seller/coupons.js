/**
 * Cloudflare Pages Edge Function: /api/marketplace/seller/coupons
 * Seller coupon creation & redemption tracking
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
    const coupons = [
      {
        code: "LAUNCH20",
        discount_type: "PERCENTAGE",
        discount_value: 20,
        times_used: 18,
        max_uses: 50,
        is_active: true,
        expires_at: "2026-12-31"
      },
      {
        code: "BLACKFRIDAY",
        discount_type: "FIXED_USD",
        discount_value: 15.00,
        times_used: 42,
        max_uses: 100,
        is_active: true,
        expires_at: "2026-11-30"
      }
    ];

    return new Response(JSON.stringify({
      success: true,
      coupons
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch coupons"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json().catch(() => ({}));
    const { code, discount_type, discount_value, max_uses, expires_at } = body;

    if (!code || !discount_value) {
      return new Response(JSON.stringify({ success: false, error: "Missing required fields" }), { status: 400 });
    }

    const cleanCode = code.toUpperCase().replace(/[^A-Z0-9_-]/g, '');

    const newCoupon = {
      code: cleanCode,
      discount_type: discount_type || "PERCENTAGE",
      discount_value: parseFloat(discount_value),
      times_used: 0,
      max_uses: parseInt(max_uses, 10) || 50,
      is_active: true,
      expires_at: expires_at || "2026-12-31"
    };

    return new Response(JSON.stringify({
      success: true,
      message: `Code promo ${cleanCode} activé avec succès !`,
      coupon: newCoupon
    }), {
      status: 201,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to create coupon"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
