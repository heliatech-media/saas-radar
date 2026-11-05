/**
 * Cloudflare Pages Edge Function: /api/marketplace/buyer/support
 * Real Buyer support requests and discussions with template creators
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
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
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

    const userTickets = (userId || email) ? await store.getUserTickets(userId, email) : [];

    return new Response(JSON.stringify({
      success: true,
      total: userTickets.length,
      tickets: userTickets
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Impossible de récupérer les tickets de support"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}

export async function onRequestPost(context) {
  try {
    const user = await getAuthUser(context);
    const store = getStore(context.env);

    if (!user || !user.email) {
      return new Response(JSON.stringify({ error: "Authentification requise pour ouvrir un ticket." }), {
        status: 401,
        headers: { "Content-Type": "application/json" }
      });
    }

    const body = await context.request.json();
    const productSlug = body.product_slug || "general";
    const subject = (body.subject || "").trim();
    const message = (body.message || "").trim();

    if (!subject || !message) {
      return new Response(JSON.stringify({ error: "Le sujet et le message sont obligatoires." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    const ticket = await store.createSupportTicket({
      userId: user.userId || `usr_${btoa(user.email).slice(0, 10)}`,
      email: user.email,
      productSlug,
      subject,
      message
    });

    return new Response(JSON.stringify({
      success: true,
      message: "✓ Votre ticket d'assistance a été ouvert. Le vendeur a été notifié par email !",
      ticket
    }), {
      status: 201,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Erreur lors de la création du ticket."
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
