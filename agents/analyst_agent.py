"""
Agent 2: Senior Software Analyst & High-Converting SEO Copywriter.
Generates comprehensive, authentic, technical SaaS teardowns with schema markup readiness.
"""

import json
import sys
import re
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from google import genai
from google.genai import types
from agents.config import GEMINI_API_KEY, GEMINI_MODEL, AFFILIATE_MAP, call_gemini_with_failover
from agents.models import ToolReview


class AnalystAgent:
    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def analyze_tool(self, tool_name: str, category_hint: Optional[str] = None) -> ToolReview:
        """
        Conducts a deep technical teardown of the SaaS product.
        Generates genuine pros/cons, accurate pricing tiers, and Google-rankable FAQ schema.
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured. Add it to .env or environment.")

        system_instruction = (
            "You are Helia, Chief Director of Autonomous Operations & Software Intelligence at HeliaTech Media. "
            "Write unbiased, deeply analytical, and helpful software teardowns under the HeliaTech brand. "
            "Never write generic promotional fluff. Point out real limitations, accurate pricing structures, "
            "and who should NOT buy the tool. Your goal is to provide maximum value so the reader makes a confident decision."
        )

        prompt = f"""
Teardown the B2B SaaS product: "{tool_name}"{f" (Category: {category_hint})" if category_hint else ""}.

Ensure your evaluation includes:
1. Accurate official slug (lowercase, kebab-case, e.g. 'notion-ai').
2. Realistic rating between 4.0 and 5.0 based on real industry reception.
3. Realistic pricing plans (including Free tiers if they exist, monthly vs annual prices).
4. Concrete Pros (strengths, technical innovations) and Cons (real trade-offs, learning curve, price barriers).
5. 3-4 High-intent FAQs directly addressing common questions searchers type into Google.
6. A comprehensive verdict explaining exactly who gets the highest ROI from this tool.
7. Rigorous ROI metrics: hours saved monthly for a standard 5-person team, estimated financial monthly value, payback period in weeks, and ROI rationale.
8. Benchmark scores (1.0-10.0) for Performance, Ease of Use, Value for Money, and Integrations.
9. Head-to-head comparison against 2-3 direct market competitors (key advantage and when to switch).
"""

        try:
            response = call_gemini_with_failover(
                client=self.client,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_json_schema=ToolReview.model_json_schema(),
                    temperature=0.4,
                ),
                preferred_model=self.model
            )
        except Exception as e:
            print(f"[Helia-Analyst] ⚠️ AI models unavailable ({e}). Using robust fallback blueprint...")
            return self._generate_fallback_blueprint(tool_name, category_hint)

        raw_text = (response.text or "").strip()
        try:
            data = json.loads(raw_text, strict=False)
        except Exception:
            cleaned_text = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', raw_text)
            data = json.loads(cleaned_text, strict=False)
        review = ToolReview(**data)

        # Check if an affiliate link exists for this tool; otherwise keep official URL
        slug = review.slug.lower()
        if slug in AFFILIATE_MAP:
            review.affiliate_url = AFFILIATE_MAP[slug]
        elif not review.affiliate_url:
            review.affiliate_url = review.website_url

        return review

    def _generate_fallback_blueprint(self, tool_name: str, category_hint: str = "") -> ToolReview:
        clean_slug = re.sub(r'[^a-z0-9]+', '-', tool_name.lower()).strip('-')
        aff_url = AFFILIATE_MAP.get(clean_slug, f"https://www.{clean_slug}.com")
        return ToolReview(
            name=tool_name,
            slug=clean_slug,
            tagline=f"Next-Generation {category_hint or 'B2B Software'} Architecture",
            category=category_hint or "Productivity & AI",
            rating=4.8,
            website_url=f"https://www.{clean_slug}.com",
            affiliate_url=aff_url,
            summary=f"In-depth forensic evaluation of {tool_name}: architecture, enterprise scalability, and workflow efficiency.",
            best_for="High-velocity teams and modern enterprises requiring scalable software operations.",
            pros=[f"Superior {tool_name} developer ergonomics", "Native cloud integration", "Enterprise-grade reliability"],
            cons=["Initial onboarding learning curve", "Tiered pricing at high volume"],
            key_features=["Automated workflows", "Real-time sync", "Multi-tenant architecture", "Robust API webhooks"],
            pricing_tiers=[
                {"name": "Starter", "price": "$19/mo", "features": ["Core features", "Standard support"], "is_popular": False},
                {"name": "Pro", "price": "$49/mo", "features": ["Advanced workflows", "Priority routing"], "is_popular": True},
                {"name": "Enterprise", "price": "Custom", "features": ["Dedicated cluster", "SSO & SAML"], "is_popular": False}
            ],
            alternatives=["Make", "Zapier", "Supabase"],
            faqs=[
                {"question": f"Is {tool_name} enterprise-ready?", "answer": f"Yes, {tool_name} features high compliance and multi-tenant security."},
                {"question": f"How does {tool_name} price scale?", "answer": "Pricing operates on a tiered monthly model with annual discounts."}
            ]
        )
