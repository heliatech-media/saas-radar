export async function GET() {
  const robotsTxt = `User-agent: *
Allow: /
Disallow: /go/

Sitemap: https://heliatech.online/sitemap.xml
`;

  return new Response(robotsTxt, {
    headers: {
      'Content-Type': 'text/plain',
    },
  });
}
