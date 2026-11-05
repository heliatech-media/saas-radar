/**
 * Cloudflare Pages Edge Function: /api/marketplace/products
 * Full-text search, multi-faceted filtering, sorting, and pagination for products
 */
import { PRODUCTS } from "../_catalog.js";

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
  });
}

export async function onRequestGet(context) {
  try {
    const url = new URL(context.request.url);
    const q = (url.searchParams.get("q") || "").toLowerCase().trim();
    const ecosystem = (url.searchParams.get("ecosystem") || "all").toLowerCase().trim();
    const category = (url.searchParams.get("category") || "all").trim();
    const priceType = (url.searchParams.get("price_type") || "all").toLowerCase().trim();
    const difficulty = (url.searchParams.get("difficulty") || "all").toLowerCase().trim();
    const sort = (url.searchParams.get("sort") || "popular").toLowerCase().trim();
    const page = Math.max(1, parseInt(url.searchParams.get("page") || "1", 10));
    const limit = Math.min(50, Math.max(1, parseInt(url.searchParams.get("limit") || "12", 10)));

    // 1. Filter
    let filtered = PRODUCTS.filter((item) => {
      // Ecosystem filter
      if (ecosystem !== "all" && item.ecosystem.toLowerCase() !== ecosystem) {
        return false;
      }

      // Category filter
      if (category !== "all" && category !== "Tous" && item.category !== category) {
        return false;
      }

      // Price type filter: free vs paid
      if (priceType === "free" && !item.is_free && item.price_usd > 0) {
        return false;
      }
      if (priceType === "paid" && (item.is_free || item.price_usd === 0)) {
        return false;
      }

      // Difficulty filter
      if (difficulty !== "all" && (item.difficulty || "intermediate").toLowerCase() !== difficulty) {
        return false;
      }

      // Search query
      if (q) {
        const title = (item.title || "").toLowerCase();
        const tagline = (item.tagline || "").toLowerCase();
        const services = (item.required_services || []).join(" ").toLowerCase();
        const creator = (item.creator?.name || "").toLowerCase();
        const cat = (item.category || "").toLowerCase();
        const match = title.includes(q) || tagline.includes(q) || services.includes(q) || creator.includes(q) || cat.includes(q);
        if (!match) return false;
      }

      return true;
    });

    // 2. Sort
    filtered.sort((a, b) => {
      if (sort === "price-asc") {
        return (a.price_usd || 0) - (b.price_usd || 0);
      }
      if (sort === "price-desc") {
        return (b.price_usd || 0) - (a.price_usd || 0);
      }
      if (sort === "rating") {
        return (b.rating || 0) - (a.rating || 0);
      }
      if (sort === "newest") {
        return (b.id || "").localeCompare(a.id || "");
      }
      // default: popular (sales count)
      return (b.sales_count || 0) - (a.sales_count || 0);
    });

    // 3. Paginate
    const total = filtered.length;
    const totalPages = Math.ceil(total / limit);
    const startIndex = (page - 1) * limit;
    const paginated = filtered.slice(startIndex, startIndex + limit);

    return new Response(JSON.stringify({
      success: true,
      total,
      page,
      limit,
      total_pages: totalPages,
      products: paginated
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=60, s-maxage=300"
      }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch products"
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}
