/**
 * Cloudflare Pages Edge Function: /api/marketplace/categories
 * Returns all active categories, ecosystems and their product counts
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

export async function onRequestGet() {
  try {
    const categoryCounts = {};
    const ecosystemCounts = {};
    let totalFree = 0;
    let totalPaid = 0;

    for (const item of PRODUCTS) {
      // Category count
      const cat = item.category || "Autre";
      categoryCounts[cat] = (categoryCounts[cat] || 0) + 1;

      // Ecosystem count
      const eco = item.ecosystem || "other";
      ecosystemCounts[eco] = (ecosystemCounts[eco] || 0) + 1;

      if (item.is_free || item.price_usd === 0) {
        totalFree++;
      } else {
        totalPaid++;
      }
    }

    const categories = Object.keys(categoryCounts).map((name) => ({
      name,
      count: categoryCounts[name]
    })).sort((a, b) => b.count - a.count);

    const ecosystems = Object.keys(ecosystemCounts).map((id) => ({
      id,
      name: id.toUpperCase(),
      count: ecosystemCounts[id]
    })).sort((a, b) => b.count - a.count);

    return new Response(JSON.stringify({
      success: true,
      total_products: PRODUCTS.length,
      total_free: totalFree,
      total_paid: totalPaid,
      categories,
      ecosystems
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "public, max-age=300, s-maxage=600"
      }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch categories"
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}
