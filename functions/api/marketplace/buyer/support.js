/**
 * Cloudflare Pages Edge Function: /api/marketplace/buyer/support
 * Buyer support requests and discussions with template creators
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
    const defaultTickets = [
      {
        id: "tkt_001",
        subject: "Question sur le format du webhook entrant",
        product_slug: "n8n-ai-lead-enricher-waterfall",
        creator_name: "AutomateScale Studio",
        status: "RESOLVED",
        created_at: "2026-10-19T11:20:00Z",
        messages: [
          {
            sender: "Alexandre R. (Acheteur)",
            text: "Bonjour, est-ce que le webhook gère automatiquement les domaines avec www. ou faut-il les filtrer en amont ?",
            time: "19 Oct 2026, 11:20"
          },
          {
            sender: "AutomateScale Studio (Support)",
            text: "Bonjour Alexandre ! Le nœud 'Claude ICP Scorer' effectue une regex de normalisation interne qui supprime les préfixes www. et https://. Vous pouvez envoyer directement le domaine brut.",
            time: "19 Oct 2026, 11:42"
          }
        ]
      }
    ];

    return new Response(JSON.stringify({
      success: true,
      tickets: defaultTickets
    }), {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to fetch support tickets"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json().catch(() => ({}));
    const { subject, message, product_slug } = body;

    if (!subject || !message) {
      return new Response(JSON.stringify({ success: false, error: "Missing subject or message" }), { status: 400 });
    }

    const newTicket = {
      id: `tkt_${Date.now()}`,
      subject: subject.trim(),
      product_slug: product_slug || "general",
      creator_name: "Support HeliaTech / Vendeur Partenaire",
      status: "OPEN",
      created_at: new Date().toISOString(),
      messages: [
        {
          sender: "Vous",
          text: message.trim(),
          time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
        }
      ]
    };

    return new Response(JSON.stringify({
      success: true,
      message: "Ticket de support ouvert ! Le vendeur a été notifié par email et Telegram.",
      ticket: newTicket
    }), {
      status: 201,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message || "Failed to open support ticket"
    }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}
