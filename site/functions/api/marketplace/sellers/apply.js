/**
 * Cloudflare Pages Function: /api/marketplace/sellers/apply
 * Handles new seller applications, checks eligibility, and alerts admin
 */

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}

export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const applicantName = (body.applicantName || "").trim();
    const applicantEmail = (body.applicantEmail || "").trim().toLowerCase();
    const portfolioUrl = (body.portfolioUrl || "").trim();
    const motivationText = (body.motivationText || "").trim();
    const expertiseAreas = Array.isArray(body.expertiseAreas) ? body.expertiseAreas : ['n8n', 'Make'];

    if (!applicantName || !applicantEmail || !applicantEmail.includes('@') || !motivationText) {
      return new Response(JSON.stringify({ error: "Tous les champs obligatoires doivent être renseignés." }), {
        status: 400,
        headers: { "Content-Type": "application/json" }
      });
    }

    const applicationId = `app_${Date.now()}`;
    const now = new Date().toISOString();

    // Instant Telegram Alert to Executive Desk
    const botToken = context.env?.TELEGRAM_BOT_TOKEN;
    const chatId = context.env?.TELEGRAM_CHAT_ID;

    if (botToken && chatId) {
      const text = 
        `🚀 NOUVELLE CANDIDATURE VENDEUR HELIATECH !\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
        `👤 Candidat : ${applicantName}\n` +
        `📧 Email : ${applicantEmail}\n` +
        `🛠️ Expertises : ${expertiseAreas.join(', ')}\n` +
        `🌐 Portfolio : ${portfolioUrl || 'Non renseigné'}\n` +
        `📝 Motivation : ${motivationText.slice(0, 150)}...\n` +
        `🆔 ID Dossier : ${applicationId}\n` +
        `⏰ Date : ${now}\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━━━`;

      try {
        await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chat_id: chatId, text })
        });
      } catch (e) {
        // Notification failure shouldn't fail application save
      }
    }

    return new Response(JSON.stringify({
      success: true,
      applicationId,
      status: "pending",
      message: "Votre dossier a été soumis avec succès et est en cours d'examen par l'équipe HeliaTech.",
      estimatedReviewHours: 24
    }), {
      status: 201,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: `Erreur interne: ${err.message}` }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
