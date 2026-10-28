import { getCollection } from 'astro:content';
import duelsData from '../data/versus-duels.json';

export async function GET() {
  const reviews = await getCollection('reviews');
  const blogPosts = await getCollection('blog');
  const baseUrl = 'https://heliatech.online';

  const staticUrls = [
    '/',
    '/deals/',
    '/radar/',
    '/awards/',
    '/versus/',
    '/calculator/',
    '/calculator/ai-pricing/',
    '/pricing-leaks/',
    '/blog/',
  ];

  const reviewUrls = reviews.map((r) => `/reviews/${r.slug}/`);
  const blogUrls = blogPosts.map((b) => `/blog/${b.slug}/`);
  const versusUrls = duelsData.map((d) => `/versus/${d.slug}/`);

  const allUrls = [...staticUrls, ...reviewUrls, ...blogUrls, ...versusUrls];

  const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allUrls
  .map(
    (url) => `  <url>
    <loc>${baseUrl}${url === '/' ? '/' : url}</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>${url === '/' || url === '/blog/' || url === '/versus/' ? 'daily' : 'weekly'}</changefreq>
    <priority>${url === '/' ? '1.0' : url.startsWith('/versus/') ? '0.85' : url.startsWith('/blog/') ? '0.9' : '0.8'}</priority>
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
