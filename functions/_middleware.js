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

  // Proceed to origin
  return context.next();
}
