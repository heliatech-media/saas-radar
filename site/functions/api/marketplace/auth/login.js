/**
 * Cloudflare Pages Function: /api/marketplace/auth/login
 * Handles user login / authentication and returns real persistent database profile
 */
import { getStore } from "../_store.js";

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
    exp: Math.floor(Date.now() / 1000) + (30 * 24 * 3600)
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
    const requestedRole = (body.role || "").toUpperCase();

    if (!email || !email.includes('@')) {
      return new Response(JSON.stringify({ error: "Adresse email professionnelle invalide." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    const adminPassword = context.env?.SENTINEL_PASSWORD || "heliatech2026secure";
    const jwtSecret = context.env?.MARKETPLACE_JWT_SECRET || "heliatech_secret_hmac_key_2026_super_secure";

    const store = getStore(context.env);

    // Look up in real database
    let dbUser = await store.getUserByEmail(email);
    let role = "USER";

    if (password && password === adminPassword) {
      role = "ADMIN";
    } else if (dbUser) {
      role = dbUser.role || "USER";
    } else if (requestedRole === "SELLER") {
      role = "SELLER";
    }

    if (!dbUser) {
      dbUser = await store.createUser({ email, name, role });
    }

    // Look up seller profile if seller
    let sellerProfile = null;
    if (role === "SELLER") {
      sellerProfile = await store.createOrUpdateSellerProfile({
        userId: dbUser.id,
        email: dbUser.email,
        storeName: `${dbUser.name} Studio`
      });
    }

    const token = await signJwt({
      userId: dbUser.id,
      email: dbUser.email,
      name: dbUser.name,
      role,
      sellerId: sellerProfile?.id || null,
      storeName: sellerProfile?.store_name || null
    }, jwtSecret);

    const isSecure = context.request.url.startsWith('https:');
    const cookieString = `ht_session=${token}; Path=/; Max-Age=2592000; HttpOnly; SameSite=Lax${isSecure ? '; Secure' : ''}`;

    return new Response(JSON.stringify({
      success: true,
      token,
      user: {
        userId: dbUser.id,
        email: dbUser.email,
        name: dbUser.name,
        role,
        sellerId: sellerProfile?.id || null,
        storeName: sellerProfile?.store_name || null,
        iban: sellerProfile?.iban || null
      }
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Set-Cookie": cookieString,
        "Access-Control-Allow-Origin": "*"
      }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: `Erreur interne: ${err.message}` }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
