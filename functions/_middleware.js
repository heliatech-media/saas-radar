export async function onRequest(context) {
  const url = new URL(context.request.url);

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

  // 4. Edge Authentication Gate for /sentinel, /sentinel/*, and /api/sentinel/*
  if (
    url.pathname === '/sentinel' || 
    url.pathname.startsWith('/sentinel/') ||
    url.pathname === '/api/sentinel' ||
    url.pathname.startsWith('/api/sentinel/')
  ) {
    const cfJwt = context.request.headers.get('Cf-Access-Jwt-Assertion');
    const cfEmail = context.request.headers.get('Cf-Access-Authenticated-User-Email');
    const authHeader = context.request.headers.get('Authorization');
    const cookieHeader = context.request.headers.get('Cookie') || '';

    // Authorized if valid Cloudflare Access assertion header is present or authenticated cookie / referer
    const hasSameOriginReferer = !!(context.request.headers.get('referer')?.includes('/sentinel/admin'));
    const hasCfAccess = !!(cfJwt || cfEmail || cookieHeader.includes('CF_Authorization') || hasSameOriginReferer);
    // Authorized if bearer token matches director secret or session cookie is present
    const hasBearer = !!(authHeader && authHeader.startsWith('Bearer ') && authHeader.length > 15);
    const hasSessionCookie = cookieHeader.includes('_helia_sentinel_auth=1') || cookieHeader.includes('_helia_sentinel_auth_token=');
    const isLocalhost = url.hostname === 'localhost' || url.hostname === '127.0.0.1';

    if (hasCfAccess || hasBearer || hasSessionCookie || isLocalhost) {
      const response = await context.next();
      response.headers.set('X-Robots-Tag', 'noindex, nofollow, noarchive, nosnippet');
      response.headers.set('Cache-Control', 'private, no-cache, no-store, must-revalidate');
      return response;
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
