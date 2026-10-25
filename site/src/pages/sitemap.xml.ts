import { getCollection } from 'astro:content';

export async function GET() {
  const reviews = await getCollection('reviews');
  const blogPosts = await getCollection('blog');
  const baseUrl = 'https://heliatech.online';

  const staticUrls = [
    '',
    '/deals',
    '/awards',
    '/versus',
    '/calculator',
    '/blueprint',
    '/partner',
    '/blog',
  ];

  const reviewUrls = reviews.map((r) => `/reviews/${r.slug}`);
  const blogUrls = blogPosts.map((b) => `/blog/${b.slug}`);
  const allUrls = [...staticUrls, ...reviewUrls, ...blogUrls];

  const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allUrls
  .map(
    (url) => `  <url>
    <loc>${baseUrl}${url}</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>${url === '' || url === '/blog' ? 'daily' : 'weekly'}</changefreq>
    <priority>${url === '' ? '1.0' : url.startsWith('/blog') ? '0.9' : '0.8'}</priority>
  </url>`
  )
  .join('\n')}
</urlset>`;

  return new Response(sitemapXml, {
    headers: {
      'Content-Type': 'application/xml',
    },
  });
}
