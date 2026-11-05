/**
 * HELIATECH DIGITAL TEMPLATES MARKETPLACE
 * Web Crypto HMAC-SHA256 Token & Session Management
 * Compatible with Cloudflare Workers / Pages Functions & Node.js
 */

import type { UserRole } from './types';
import type { AuthContext } from './permissions';

const DEFAULT_SECRET = 'heliatech_secret_hmac_key_2026_super_secure';

function getSecret(envSecret?: string): string {
  return envSecret || (typeof process !== 'undefined' ? process.env.MARKETPLACE_JWT_SECRET : '') || DEFAULT_SECRET;
}

/**
 * Base64 URL Encoder / Decoder
 */
function base64UrlEncode(str: string): string {
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function base64UrlDecode(str: string): string {
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) str += '=';
  return atob(str);
}

/**
 * Sign payload with Web Crypto API HMAC-SHA256
 */
export async function signToken(payload: Record<string, any>, secretKey?: string): Promise<string> {
  const secret = getSecret(secretKey);
  const enc = new TextEncoder();
  const header = { alg: 'HS256', typ: 'JWT' };

  const encodedHeader = base64UrlEncode(JSON.stringify(header));
  const encodedPayload = base64UrlEncode(JSON.stringify({
    ...payload,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (30 * 24 * 3600) // 30-day session
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

/**
 * Verify and decode token with Web Crypto API
 */
export async function verifyToken(token: string, secretKey?: string): Promise<AuthContext | null> {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;

    const [headerB64, payloadB64, signatureB64] = parts;
    const dataToVerify = `${headerB64}.${payloadB64}`;
    const secret = getSecret(secretKey);
    const enc = new TextEncoder();

    const key = await crypto.subtle.importKey(
      'raw',
      enc.encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify']
    );

    // Decode signature
    const binarySignature = atob(signatureB64.replace(/-/g, '+').replace(/_/g, '/'));
    const sigBytes = new Uint8Array(binarySignature.length);
    for (let i = 0; i < binarySignature.length; i++) {
      sigBytes[i] = binarySignature.charCodeAt(i);
    }

    const isValid = await crypto.subtle.verify('HMAC', key, sigBytes, enc.encode(dataToVerify));
    if (!isValid) return null;

    const payload = JSON.parse(base64UrlDecode(payloadB64));
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
      return null; // Expired
    }

    return {
      userId: payload.userId,
      email: payload.email,
      role: (payload.role as UserRole) || 'USER',
      sellerId: payload.sellerId
    };
  } catch (e) {
    return null;
  }
}

/**
 * Extracts and verifies auth context from standard Request headers
 */
export async function getAuthContextFromRequest(request: Request, secretKey?: string): Promise<AuthContext | null> {
  // 1. Check Authorization Bearer header
  const authHeader = request.headers.get('Authorization') || request.headers.get('authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.slice(7).trim();
    return verifyToken(token, secretKey);
  }

  // 2. Check cookie: ht_session
  const cookieHeader = request.headers.get('Cookie') || request.headers.get('cookie') || '';
  const match = cookieHeader.match(/ht_session=([^;]+)/);
  if (match) {
    return verifyToken(match[1], secretKey);
  }

  return null;
}
