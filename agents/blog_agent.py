"""
Agent 4: Editorial & Affiliate Blog Architect (Helia Tech Elite Content Factory).
Crafts in-depth, high-converting storytelling articles dedicated to affiliated software:
evolution/genesis, business superpowers, step-by-step practical workshops, and pros/cons.
"""

import json
from datetime import datetime
from google import genai
from google.genai import types
from agents.config import GEMINI_API_KEY, GEMINI_MODEL, AFFILIATE_MAP
from agents.models import ToolReview, BlogPost, AffiliateCTA


class BlogAgent:
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = model

    def write_tool_masterclass(self, review: ToolReview) -> BlogPost:
        """
        Generates a comprehensive editorial blog post dedicated to the specified software tool.
        """
        affiliate_url = AFFILIATE_MAP.get(review.slug, f"/go/{review.slug}")
        prompt = f"""
Tu es le rédacteur en chef d'investigation tech et stratège B2B pour le média HELIA TECH (heliatech.online).
Rédige un article de fond captivant et ultra-complet dédié au logiciel suivant :

Nom de l'outil : {review.name}
Slug : {review.slug}
Catégorie : {review.category}
Tagline : {review.tagline}
Pitch : {review.summary}
Forces : {', '.join(review.pros)}
Faiblesses : {', '.join(review.cons)}
Lien affilié : {affiliate_url}

Consignes éditoriales strictes :
1. Style journalistique immersif, captivant, d'autorité (style The Verge, Wired, TechCrunch).
2. PAS de blueprints abstraits ou de pseudo-code serveur. C'est du VRAI BLOGGING d'entreprise et de productivité.
3. Structure obligatoire de l'article :
   - Introduction percutante avec drop-cap naturel : raconte la douleur du marché avant ce logiciel.
   - 1. La Genèse & L'Évolution : qui l'a créé, d'où vient l'idée, comment le logiciel a transformé son marché.
   - 2. Les Super-Pouvoirs Business : 3 ou 4 fonctionnalités majeures qui changent la vie d'une entreprise.
   - 3. L'Atelier Pratique (Tutoriel Pas-à-Pas) : un cas concret en 3 ou 4 étapes pour que le lecteur puisse l'appliquer en 15 minutes.
   - 4. Analyse Critique & Limites : tableau des points forts et des vrais compromis pour rester 100% objectif et crédible.
   - 5. Verdict & Synthèse HeliaTech : recommandation honnête et appel à l'action.
4. Intègre une citation inspirante en blockquote (> citation).
5. Fournis un objet JSON strict correspondant au schéma BlogPost :
{{
  "title": "Titre journalistique captivant (ex: 'ClickUp 3.0 : L'Histoire d'une Révolution et le Guide Pratique pour Dompter Vos Projets en 2026')",
  "slug": "{review.slug}-evolution-guide-2026",
  "description": "Courte description SEO (150-160 caractères) percutante.",
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "author": "HELIA TECH",
  "category": "{review.category}",
  "tags": ["{review.name}", "Productivité", "SaaS", "Guide Pratique", "Automatisation"],
  "readingTime": "11 MIN",
  "tool_slug": "{review.slug}",
  "tldr": [
    "Point clé 1 sur l'origine et la rupture du logiciel",
    "Point clé 2 sur les super-pouvoirs et gains de productivité",
    "Point clé 3 sur le résultat de l'atelier pratique"
  ],
  "affiliate_cta": {{
    "badge": "OFFRE OFFICIELLE HELIATECH",
    "title": "Testez {review.name} gratuitement",
    "description": "Activez votre compte pour explorer les fonctionnalités avancées et booster votre productivité.",
    "button_text": "Découvrir {review.name} gratuitement ➔",
    "url": "{affiliate_url}"
  }},
  "markdown_content": "Le corps entier de l'article en pur Markdown avec les titres H2, H3, listes, tableaux, citations et explications détaillées."
}}
Réponds UNIQUEMENT avec le JSON valide, sans texte additionnel ni délimiteurs markdown comme ```json.
"""
        if not self.client:
            raise ValueError("GEMINI_API_KEY non configurée.")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json",
            )
        )

        data = json.loads(response.text)
        return BlogPost(**data)
