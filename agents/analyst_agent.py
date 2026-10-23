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
from agents.config import GEMINI_API_KEY, GEMINI_MODEL, AFFILIATE_MAP
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
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_json_schema=ToolReview.model_json_schema(),
                    temperature=0.4,
                ),
            )
        except Exception as e:
            print(f"[Helia-Analyst] ⚠️ Primary model {self.model} busy ({e}). Switching to high-throughput fallback: gemini-3.5-flash-lite...")
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_json_schema=ToolReview.model_json_schema(),
                    temperature=0.4,
                ),
            )

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
