"""
Agent 1: Market & Intent Radar (Senior Discovery Specialist).
Identifies high-converting SaaS products, search intents, and recurring affiliate opportunities.
"""

import json
import os
import re
from pathlib import Path
from typing import List, Optional
from google import genai
from google.genai import types
from agents.config import GEMINI_API_KEY, GEMINI_MODEL, TARGET_NICHES
from agents.models import RadarKeyword


class RadarAgent:
    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def get_existing_tool_slugs(self) -> List[str]:
        """Scans the local review directory to prevent duplicate discoveries."""
        reviews_dir = Path(__file__).resolve().parent.parent / "site" / "src" / "content" / "reviews"
        if not reviews_dir.exists():
            return []
        return [f.stem for f in reviews_dir.glob("*.md")]

    def get_seed_tools(self) -> List[dict]:
        """Returns verified, top-tier SaaS tools with known high-paying affiliate programs."""
        tools = []
        for niche in TARGET_NICHES:
            for tool_name in niche["seed_tools"]:
                tools.append({
                    "name": tool_name,
                    "category": niche["category"],
                    "commission": niche["commission_range"],
                })
        return tools

    def discover_trending_opportunities(self, category: Optional[str] = None, count: int = 2) -> List[RadarKeyword]:
        """
        Uses Gemini to discover trending, high-converting B2B SaaS software with active affiliate programs
        and high commercial search volume, strictly avoiding existing covered tools.
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured. Add it to .env or environment.")

        existing = self.get_existing_tool_slugs()
        exclude_str = ", ".join(existing) if existing else "none"

        prompt = f"""
You are Helia-Radar, Chief Market Intelligence and Opportunity Discovery Agent at HeliaTech Media.
Identify {count} high-growth, high-converting B2B SaaS tools {"in category: " + category if category else "across high-margin B2B SaaS niches (AI, DevTools, E-Commerce, Marketing, Automation)"}.

CRITICAL MANDATES:
1. High commercial buyer intent (users searching for pricing, teardowns, and alternatives).
2. Known for having an active, high-paying recurring affiliate or partner program (20% to 50% recurring MRR, e.g. via PartnerStack, Rewardful, FirstPromoter, or direct).
3. DO NOT include any of the following software tools because they have ALREADY been evaluated:
[{exclude_str}]
4. Focus on breakout, established modern platforms (e.g. Supabase, Vercel, Framer, Typeform, Linear, Apollo.io, PhantomBuster, Beehiiv, Lemlist, Lovable, v0).

Provide the output strictly conforming to the requested JSON schema.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema={
                        "type": "ARRAY",
                        "items": RadarKeyword.model_json_schema(),
                    },
                    temperature=0.7,
                ),
            )
        except Exception as e:
            print(f"[Helia-Radar] ⚠️ Primary model {self.model} busy ({e}). Switching to high-throughput fallback: gemini-3.5-flash-lite...")
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema={
                        "type": "ARRAY",
                        "items": RadarKeyword.model_json_schema(),
                    },
                    temperature=0.7,
                ),
            )

        try:
            data = json.loads(response.text)
            keywords = [RadarKeyword(**item) for item in data]
            print(f"[Helia-Radar] 🛰️ Successfully discovered {len(keywords)} new candidate tools: {[k.tool_name for k in keywords]}")
            return keywords
        except Exception as e:
            print(f"[Helia-Radar] ❌ Error parsing radar response: {e}")
            return []
