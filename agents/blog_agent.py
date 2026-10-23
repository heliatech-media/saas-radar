"""
Agent 4: Editorial & Affiliate Blog Architect (Helia Tech Elite Content Factory).
Crafts in-depth, high-converting storytelling articles dedicated to affiliated software:
evolution/genesis, business superpowers, step-by-step practical workshops, and pros/cons.
Generates 100% English content.
"""

import json
from datetime import datetime
from google import genai
from google.genai import types
from agents.config import GEMINI_API_KEY, GEMINI_MODEL, AFFILIATE_MAP
from agents.models import ToolReview, BlogPost, AffiliateCTA
from agents.article_layout_agent import ArticleLayoutAgent
from agents.image_generator_agent import ImageGeneratorAgent


class BlogAgent:
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = model

    def write_tool_masterclass(self, review: ToolReview) -> BlogPost:
        """
        Generates a comprehensive editorial blog post dedicated to the specified software tool in 100% English.
        """
        affiliate_url = AFFILIATE_MAP.get(review.slug, f"/go/{review.slug}")
        prompt = f"""
You are the Chief Investigative Tech Editor and Enterprise B2B Strategist for HELIA TECH (heliatech.online).
Write an in-depth, captivating, high-ranking 100% ENGLISH masterclass article dedicated to the following software:

Tool Name: {review.name}
Slug: {review.slug}
Category: {review.category}
Tagline: {review.tagline}
Pitch: {review.summary}
Strengths: {', '.join(review.pros)}
Limitations: {', '.join(review.cons)}
Affiliate Redirect: {affiliate_url}

Strict Editorial Directives:
1. Pure, native, high-impact American English (Wired / The Verge / TechCrunch depth).
2. NO abstract code sandboxes or server blueprints. This is REAL BUSINESS SOFTWARE BLOGGING.
3. Mandatory Article Structure:
   - Punchy opening with a compelling drop-cap: describe the market pain, tool fragmentation, or human bottleneck before this tool existed.
   - 1. The Genesis & Evolution: the founders, the spark behind the creation, and how it disrupted legacy dinosaurs.
   - 2. Core Business Superpowers: 3 or 4 high-value capabilities that save companies thousands of dollars/hours.
   - 3. Hands-on Workshop (15-Minute Blueprint): a practical, step-by-step tutorial the reader can replicate today.
   - 4. Critical Assessment & Trade-offs: an objective table comparing strengths and real limitations.
   - 5. HeliaTech Final Verdict & Recommendation: authentic executive recommendation with a call to action.
4. Include an inspiring pull quote in markdown blockquote format (> Quote).
5. Output MUST be a valid JSON object strictly matching the following BlogPost schema:
{{
  "title": "Captivating journalistic title (e.g., 'ClickUp: The Genesis of the Workspace OS and the Hands-on Guide to Project Velocity in 2026')",
  "slug": "{review.slug}-evolution-guide-2026",
  "description": "Punchy 150-160 character SEO meta description in English.",
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "author": "HELIA TECH",
  "category": "{review.category}",
  "tags": ["{review.name}", "Productivity", "SaaS", "Automation", "B2B Software"],
  "readingTime": "11 MIN",
  "tool_slug": "{review.slug}",
  "tldr": [
    "Key takeaway 1 regarding origin and market disruption",
    "Key takeaway 2 regarding productivity superpowers and ROI",
    "Key takeaway 3 regarding the hands-on workshop takeaway"
  ],
  "affiliate_cta": {{
    "badge": "OFFICIAL HELIATECH PARTNERSHIP",
    "title": "Experience {review.name} Free",
    "description": "Activate your account to unlock advanced enterprise features and streamline team velocity.",
    "button_text": "Claim Your Free {review.name} Account ➔",
    "url": "{affiliate_url}"
  }},
  "markdown_content": "Full markdown body of the article in 100% English with H2, H3, bullet points, markdown tables, quotes, and thorough analysis."
}}
Reply ONLY with the valid JSON object, without any surrounding markdown code fences like ```json.
"""
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured.")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json",
            )
        )

        raw_text = (response.text or "").strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        try:
            data = json.loads(raw_text, strict=False)
        except Exception:
            import re
            cleaned_text = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', raw_text)
            data = json.loads(cleaned_text, strict=False)

        post = BlogPost(**data)
        
        # 1. Generate dedicated relative hero artwork via Helia-VisualArtist
        try:
            artist = ImageGeneratorAgent(api_key=self.client.api_key if self.client else "")
            artist.generate_article_hero_image(
                tool_name=review.name,
                tool_slug=review.slug,
                title=post.title,
                category=review.category
            )
            post.image = f"/images/blog/{review.slug}.svg"
        except Exception as e:
            print(f"[Helia-ContentFactory] ⚠️ Artwork generation note: {e}")
            post.image = f"/images/blog/{review.slug}.svg"

        # 2. Apply layout & visual polish via ArticleLayoutAgent
        stylist = ArticleLayoutAgent()
        post.markdown_content = stylist.beautify_markdown(
            post.markdown_content,
            tool_name=review.name,
            tool_slug=review.slug,
            category=review.category
        )
        return post
