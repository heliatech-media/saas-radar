/**
 * Cloudflare Pages Function: /api/marketplace/auth/logout
 * Destroys session cookie
 */

export async function onRequestPost() {
  return new Response(JSON.stringify({ success: true, message: "Déconnexion réussie" }), {
    status: 200,
    headers: {
      "Content-Type": "application/json",
      "Set-Cookie": "ht_session=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax",
      "Access-Control-Allow-Origin": "*"
    }
  });
}
