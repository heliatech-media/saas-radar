/**
 * HELIATECH DIGITAL TEMPLATES MARKETPLACE
 * Secure Private Asset Storage & Signed Ephemeral Download Token Generator
 * Ensures no digital files (.json, .zip, .sql) are ever exposed in public directories
 */

export interface SignedTokenPayload {
  userId: string;
  productSlug: string;
  purchaseId: string;
  exp: number; // Unix timestamp
  nonce: string;
}

export class DigitalAssetStorage {
  private secret: string;

  constructor(secret = "heliatech_ephemeral_download_secret_2026") {
    this.secret = secret;
  }

  /**
   * Generates a signed ephemeral token valid for 15 minutes (900 seconds)
   */
  async generateDownloadToken(userId: string, productSlug: string, purchaseId: string, ttlSeconds = 900): Promise<string> {
    const payload: SignedTokenPayload = {
      userId,
      productSlug,
      purchaseId,
      exp: Math.floor(Date.now() / 1000) + ttlSeconds,
      nonce: Math.random().toString(36).substring(2, 10)
    };

    const payloadJson = JSON.stringify(payload);
    const payloadB64 = btoa(payloadJson).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

    const enc = new TextEncoder();
    const key = await crypto.subtle.importKey(
      'raw',
      enc.encode(this.secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    );

    const sig = await crypto.subtle.sign('HMAC', key, enc.encode(payloadB64));
    const sigB64 = btoa(String.fromCharCode(...new Uint8Array(sig))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

    return `${payloadB64}.${sigB64}`;
  }

  /**
   * Verifies the signed download token
   */
  async verifyDownloadToken(token: string): Promise<SignedTokenPayload | null> {
    try {
      const parts = token.split('.');
      if (parts.length !== 2) return null;
      const [payloadB64, sigB64] = parts;

      const enc = new TextEncoder();
      const key = await crypto.subtle.importKey(
        'raw',
        enc.encode(this.secret),
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['verify']
      );

      const binarySig = atob(sigB64.replace(/-/g, '+').replace(/_/g, '/'));
      const sigBytes = new Uint8Array(binarySig.length);
      for (let i = 0; i < binarySig.length; i++) {
        sigBytes[i] = binarySig.charCodeAt(i);
      }

      const isValid = await crypto.subtle.verify('HMAC', key, sigBytes, enc.encode(payloadB64));
      if (!isValid) return null;

      const payloadJson = atob(payloadB64.replace(/-/g, '+').replace(/_/g, '/'));
      const payload: SignedTokenPayload = JSON.parse(payloadJson);

      // Check expiration
      if (payload.exp < Math.floor(Date.now() / 1000)) return null;

      return payload;
    } catch (e) {
      return null;
    }
  }
}

export const assetStorage = new DigitalAssetStorage();
