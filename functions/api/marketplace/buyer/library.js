/**
 * Cloudflare Pages Edge Function: /api/marketplace/buyer/library
 * Buyer's digital entitlements, active licenses, versions, and update statuses
 * Connected to persistent Database Store
 */
import { getStore } from "../_store.js";

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

async function getAuthUser(context) {
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
  return await verifyJwt(token, jwtSecret);
}

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
    const user = await getAuthUser(context);
    const store = getStore(context.env);

    const userId = user?.userId || user?.sub || "";
    const email = user?.email || "";

    // Query real user purchases from database
    const userPurchases = (userId || email) ? await store.getUserPurchases(userId, email) : [];

    return new Response(JSON.stringify({
      success: true,
      user_id: userId,
      email: email,
      is_authenticated: Boolean(user),
      total_items: userPurchases.length,
      library: userPurchases
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
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
