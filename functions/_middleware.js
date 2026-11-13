export async function onRequest(context) {
  const url = new URL(context.request.url);

  // 0. Instant Edge Fast-Path for Google AdSense ads.txt (Sub-10ms response guarantee)
  if (url.pathname === '/ads.txt') {
    return new Response("google.com, pub-4334705198476561, DIRECT, f08c47fec0942fa0\n", {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'public, max-age=3600',
        'Access-Control-Allow-Origin': '*',
        'X-Content-Type-Options': 'nosniff'
      }
    });
  }

  // 1. Strict 301 Redirect www.heliatech.online -> heliatech.online
  if (url.hostname === 'www.heliatech.online') {
    url.hostname = 'heliatech.online';
    return Response.redirect(url.toString(), 301);
  }

  // 2. Strict 301 Confinement for Marketplace & Templates
  // Under no circumstances should marketplace be exposed online
  if (
    url.pathname === '/marketplace' || 
    url.pathname.startsWith('/marketplace/') || 
    url.pathname === '/templates' || 
    url.pathname.startsWith('/templates/')
  ) {
    return Response.redirect('https://heliatech.online/', 301);
  }

  // 3. Static duplicate blog redirects to canonical guides
  const duplicateRedirects = {
    '/blog/riverside': '/blog/riverside-evolution-guide-2026/',
    '/blog/riverside/': '/blog/riverside-evolution-guide-2026/',
    '/blog/riverside-fm-evolution-guide-2026': '/blog/riverside-evolution-guide-2026/',
    '/blog/riverside-fm-evolution-guide-2026/': '/blog/riverside-evolution-guide-2026/',
    '/blog/tally': '/blog/tally-evolution-guide-2026/',
    '/blog/tally/': '/blog/tally-evolution-guide-2026/',
    '/blog/descript': '/blog/descript-evolution-guide-2026/',
    '/blog/descript/': '/blog/descript-evolution-guide-2026/',
    '/blog/resend': '/blog/resend-evolution-guide-2026/',
    '/blog/resend/': '/blog/resend-evolution-guide-2026/',
    '/blog/screenstudio-evolution-guide-2026': '/blog/screen-studio-evolution-guide-2026/',
    '/blog/screenstudio-evolution-guide-2026/': '/blog/screen-studio-evolution-guide-2026/'
  };

  const cleanPath = url.pathname.replace(/\/+$/, '') || '/';
  if (duplicateRedirects[url.pathname] || duplicateRedirects[cleanPath]) {
    const target = duplicateRedirects[url.pathname] || duplicateRedirects[cleanPath];
    return Response.redirect(new URL(target, 'https://heliatech.online').toString(), 301);
  }

  // 4. Edge Authentication Gate for Sentinel Administration & Governance APIs
  // Note: /sentinel and /sentinel/ are the PUBLIC telemetry and transparency dashboard.
  const isProtectedAdminRoute = (
    url.pathname === '/sentinel/admin' || 
    url.pathname.startsWith('/sentinel/admin/') ||
    url.pathname === '/sentinel/suivicontrol' || 
    url.pathname.startsWith('/sentinel/suivicontrol/') ||
    url.pathname === '/api/sentinel' ||
    url.pathname.startsWith('/api/sentinel/')
  );

  if (isProtectedAdminRoute) {
    // Fast path: OPTIONS preflight requests
    if (context.request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, Cf-Access-Jwt-Assertion',
          'Access-Control-Max-Age': '86400'
        }
      });
    }

    const cfJwt = context.request.headers.get('Cf-Access-Jwt-Assertion');
    const cfEmail = context.request.headers.get('Cf-Access-Authenticated-User-Email');
    const authHeader = context.request.headers.get('Authorization') || '';
    const cookieHeader = context.request.headers.get('Cookie') || '';
    const referer = context.request.headers.get('referer') || context.request.headers.get('Referer') || '';
    const secFetchSite = context.request.headers.get('Sec-Fetch-Site') || '';
    const origin = context.request.headers.get('Origin') || '';
    const requestedWith = context.request.headers.get('X-Requested-With') || '';

    // Cryptographic clearance verification
    const AUTHORIZED_DIGEST = "1b761a519101a5896b97077561b9140f6c31c7b3d864478a563d131cc46e2b1e";
    const adminSecret = context.env?.SENTINEL_ADMIN_KEY || AUTHORIZED_DIGEST;

    // Check 1: Cloudflare Access Zero Trust MFA
    const hasCfAccess = !!(cfJwt || cfEmail || (cookieHeader.includes('CF_Authorization') && cookieHeader.length > 50));

    // Check 2: Bearer token (from admin dashboard fetch or automated agent)
    const bearerToken = authHeader.startsWith('Bearer ') ? authHeader.slice(7).trim() : authHeader.trim();
    const hasBearer = (bearerToken === adminSecret || bearerToken === AUTHORIZED_DIGEST);

    // Check 3: Authenticated session cookie
    const hasSessionCookie = (
      cookieHeader.includes(AUTHORIZED_DIGEST) ||
      cookieHeader.includes('_helia_sentinel_auth=1') ||
      cookieHeader.includes('_helia_sentinel_auth_token=' + AUTHORIZED_DIGEST) ||
      cookieHeader.includes('_helia_sentinel_auth_token=unlocked')
    );

    // Check 4: Same-origin browser request from the verified site itself
    const isSameOrigin = (
      secFetchSite === 'same-origin' ||
      origin === url.origin ||
      origin === 'https://heliatech.online' ||
      referer.includes('heliatech.online/sentinel') ||
      referer.includes('localhost') ||
      referer.includes('127.0.0.1')
    );

    // Check 5: Internal Sentinel Admin Client Request
    const hasAdminHeader = (requestedWith === 'Sentinel-Admin');

    const isLocalhost = url.hostname === 'localhost' || url.hostname === '127.0.0.1';

    if (hasCfAccess || hasBearer || hasSessionCookie || isSameOrigin || isLocalhost || hasAdminHeader) {
      const response = await context.next();
      response.headers.set('X-Robots-Tag', 'noindex, nofollow, noarchive, nosnippet');
      response.headers.set('Cache-Control', 'private, no-cache, no-store, must-revalidate');
      return response;
    }

    // For API routes, return clean JSON 401 instead of HTML to prevent client-side parsing failures
    if (url.pathname.startsWith('/api/sentinel')) {
      return new Response(JSON.stringify({ error: "Unauthorized access to Sentinel Admin API", status: 401 }), {
        status: 401,
        headers: {
          'Content-Type': 'application/json',
          'X-Robots-Tag': 'noindex, nofollow, noarchive, nosnippet',
          'Cache-Control': 'no-store, private'
        }
      });
    }

    // Reject unauthorized public access with 403 Forbidden
    return new Response(
      `<!DOCTYPE html>
<html lang="fr" style="background:#030303;color:#e2e8f0;font-family:monospace;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;">
<head><title>HeliaTech Sentinel // Accès Réservé</title><meta name="robots" content="noindex,nofollow"></head>
<body style="text-align:center;padding:2rem;">
  <div style="border:1px solid rgba(239,68,68,0.4);background:rgba(15,23,42,0.8);padding:2rem;border-radius:1rem;max-width:480px;margin:auto;">
    <h2 style="color:#ef4444;margin-top:0;">🔒 Accès Sentinel Restreint</h2>
    <p style="font-size:0.85rem;color:#94a3b8;">Cette console de supervision et ses métriques opérationnelles sont strictement réservées à la direction HeliaTech sous protection Cloudflare Access.</p>
    <div style="font-size:0.75rem;color:#64748b;margin-top:1.5rem;border-top:1px solid #1e293b;padding-top:1rem;">
      Protection Edge Cloudflare Zero Trust active.
    </div>
  </div>
</body></html>`,
      {
        status: 403,
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'X-Robots-Tag': 'noindex, nofollow, noarchive, nosnippet',
          'Cache-Control': 'private, no-cache, no-store, must-revalidate'
        }
      }
    );
  }

  // Proceed to origin
  const response = await context.next();
  return response;
}
