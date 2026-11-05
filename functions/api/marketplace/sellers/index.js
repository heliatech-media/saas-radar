/**
 * Cloudflare Pages Edge Function: /api/marketplace/sellers
 * Returns verified sellers and their published blueprints
 */
import { PRODUCTS } from "../_catalog.js";

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    }
  });
}

export async function onRequestGet(context) {
  try {
    const url = new URL(context.request.url);
    const slug = (url.searchParams.get("slug") || "").toLowerCase().trim();

    // Map unique sellers
    const sellersMap = new Map();

    for (const item of PRODUCTS) {
      if (!item.creator) continue;
      const sSlug = (item.creator.slug || item.creator.name.toLowerCase().replace(/[^a-z0-9]+/g, '-')).toLowerCase();

      if (!sellersMap.has(sSlug)) {
        sellersMap.set(sSlug, {
          slug: sSlug,
          name: item.creator.name,
          badge: item.creator.badge || "Verified Creator",
          avatar: item.creator.avatar,
          bio: item.creator.bio || "",
          website: item.creator.website || null,
          github: item.creator.github || null,
          linkedin: item.creator.linkedin || null,
          total_sales: 0,
          total_products: 0,
          ratings_sum: 0,
          blueprints: []
        });
      }

      const seller = sellersMap.get(sSlug);
      seller.total_sales += (item.sales_count || 0);
      seller.total_products += 1;
      seller.ratings_sum += (item.rating || 5.0);
      seller.blueprints.push({
        id: item.id,
        slug: item.slug,
        title: item.title,
        tagline: item.tagline,
        ecosystem: item.ecosystem,
        category: item.category,
        price_usd: item.price_usd,
        is_free: item.is_free,
        rating: item.rating,
        reviews_count: item.reviews_count,
        sales_count: item.sales_count
      });
    }

    // Format ratings
    for (const seller of sellersMap.values()) {
      seller.avg_rating = seller.total_products > 0
        ? parseFloat((seller.ratings_sum / seller.total_products).toFixed(2))
        : 5.0;
      delete seller.ratings_sum;
    }

    // Single seller query
    if (slug) {
      const found = sellersMap.get(slug);
      if (!found) {
        return new Response(JSON.stringify({
          success: false,
          error: "Seller not found"
        }), {
          status: 404,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
          }
        });
      }

      return new Response(JSON.stringify({
        success: true,
        seller: found
      }), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
          "Cache-Control": "public, max-age=120"
        }
      });
    }

    // All sellers
    const sellersList = Array.from(sellersMap.values()).sort((a, b) => b.total_sales - a.total_sales);

    return new Response(JSON.stringify({
      success: true,
      total_sellers: sellersList.length,
      sellers: sellersList
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=300"
      }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch sellers"
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}
