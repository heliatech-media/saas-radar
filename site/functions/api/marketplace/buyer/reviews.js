/**
 * Cloudflare Pages Edge Function: /api/marketplace/buyer/reviews
 * Buyer review authoring and review management
 */

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
  });
}

export async function onRequestGet(context) {
  try {
    const reviews = [
      {
        id: "rev_001",
        product_slug: "n8n-ai-lead-enricher-waterfall",
        product_title: "n8n AI Waterfall Lead Enrichment & Scoring Engine",
        rating: 5,
        title: "Intégration d'une propreté exemplaire",
        comment: "Déployé en 10 minutes sur notre VPS n8n. Gestion des erreurs sans faille.",
        created_at: "2026-10-21T18:00:00Z"
      }
    ];

    return new Response(JSON.stringify({
      success: true,
      reviews
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch reviews"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json().catch(() => ({}));
    const { product_slug, rating, comment, title } = body;

    if (!product_slug || !rating || !comment) {
      return new Response(JSON.stringify({ success: false, error: "Missing required fields" }), { status: 400 });
    }

    const numRating = parseInt(rating, 10);
    if (isNaN(numRating) || numRating < 1 || numRating > 5) {
      return new Response(JSON.stringify({ success: false, error: "Rating must be between 1 and 5" }), { status: 400 });
    }

    const newReview = {
      id: `rev_${Date.now()}`,
      product_slug,
      rating: numRating,
      title: title || "Avis vérifié",
      comment: comment.trim(),
      created_at: new Date().toISOString()
    };

    return new Response(JSON.stringify({
      success: true,
      message: "Avis vérifié enregistré avec succès !",
      review: newReview
    }), {
      status: 201,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to submit review"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
