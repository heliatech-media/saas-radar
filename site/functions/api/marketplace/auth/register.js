/**
 * Cloudflare Pages Function: /api/marketplace/auth/register
 * Handles new user registration (Buyer or Seller) with HMAC-SHA256 session token
 */

function base64UrlEncode(str) {
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function signJwt(payload, secret) {
  const enc = new TextEncoder();
  const header = { alg: 'HS256', typ: 'JWT' };
  const encodedHeader = base64UrlEncode(JSON.stringify(header));
  const encodedPayload = base64UrlEncode(JSON.stringify({
    ...payload,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (30 * 24 * 3600) // 30 days session
  }));

  const dataToSign = `${encodedHeader}.${encodedPayload}`;
  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const signature = await crypto.subtle.sign('HMAC', key, enc.encode(dataToSign));
  const signatureArray = Array.from(new Uint8Array(signature));
  const signatureBase64 = base64UrlEncode(String.fromCharCode.apply(null, signatureArray));

  return `${dataToSign}.${signatureBase64}`;
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const email = (body.email || "").trim().toLowerCase();
    const name = (body.name || "").trim() || email.split('@')[0];
    const password = body.password || "";
    const accountType = (body.accountType || "buyer").toLowerCase();
    const storeName = (body.storeName || "").trim();
    const specialty = (body.specialty || "n8n").trim();
    const termsAccepted = !!body.termsAccepted;

    if (!email || !email.includes('@')) {
      return new Response(JSON.stringify({ error: "Veuillez fournir une adresse email valide." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    if (!password || password.length < 6) {
      return new Response(JSON.stringify({ error: "Le mot de passe doit contenir au moins 6 caractères." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    if (!termsAccepted) {
      return new Response(JSON.stringify({ error: "Veuillez accepter les conditions d'utilisation." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    const jwtSecret = context.env?.MARKETPLACE_JWT_SECRET || "heliatech_secret_hmac_key_2026_super_secure";

    const isSeller = accountType === 'seller';
    const role = isSeller ? 'SELLER' : 'USER';
    const userId = `usr_${btoa(email).slice(0, 18).replace(/[^a-zA-Z0-9]/g, 'x')}`;
    const sellerId = isSeller ? `seller_${btoa(email).slice(0, 14).replace(/[^a-zA-Z0-9]/g, 's')}` : null;

    const token = await signJwt({
      userId,
      email,
      name,
      role,
      sellerId,
      storeName: storeName || (isSeller ? `${name} Studio` : null),
      specialty
    }, jwtSecret);

    const isSecure = context.request.url.startsWith('https:');
    const cookieString = `ht_session=${token}; Path=/; Max-Age=2592000; HttpOnly; SameSite=Lax${isSecure ? '; Secure' : ''}`;

    return new Response(JSON.stringify({
      success: true,
      message: isSeller ? "Compte créateur activé avec succès !" : "Compte membre créé avec succès !",
      token,
      user: {
        userId,
        email,
        name,
        role,
        sellerId,
        storeName: storeName || (isSeller ? `${name} Studio` : null),
        specialty
      },
      redirectTo: isSeller ? "/seller/" : "/dashboard/"
    }), {
      status: 201,
      headers: {
        "Content-Type": "application/json",
        "Set-Cookie": cookieString,
        "Access-Control-Allow-Origin": "*"
      }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: `Erreur interne lors de l'inscription: ${err.message}` }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
