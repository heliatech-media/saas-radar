export async function GET() {
  const robotsTxt = `User-agent: *
Allow: /
Disallow: /go/
Disallow: /sentinel/
Disallow: /api/
Disallow: /templates/
Disallow: /dashboard/
Disallow: /seller/
Disallow: /sell/
Disallow: /register/
Disallow: /login/
Disallow: /creator/
Disallow: /checkout/
Disallow: /admin/

User-agent: Googlebot
Allow: /
Disallow: /go/
Disallow: /sentinel/
Disallow: /api/
Disallow: /templates/
Disallow: /dashboard/
Disallow: /seller/
Disallow: /sell/
Disallow: /register/
Disallow: /login/
Disallow: /creator/
Disallow: /checkout/
Disallow: /admin/

User-agent: Bingbot
Allow: /
Disallow: /go/
Disallow: /sentinel/
Disallow: /api/
Disallow: /templates/
Disallow: /dashboard/
Disallow: /seller/
Disallow: /sell/
Disallow: /register/
Disallow: /login/
Disallow: /creator/
Disallow: /checkout/
Disallow: /admin/

Sitemap: https://heliatech.online/sitemap.xml
`;

  return new Response(robotsTxt, {
    headers: {
      'Content-Type': 'text/plain',
    },
  });
}
