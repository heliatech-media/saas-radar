"""
Agent 1: Market & Intent Radar (Senior Discovery Specialist).
Identifies high-converting SaaS products, search intents, and recurring affiliate opportunities.
"""

import json
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

    def discover_trending_opportunities(self, category: Optional[str] = None, count: int = 5) -> List[RadarKeyword]:
        """
        Uses Gemini to discover trending B2B SaaS software with active affiliate programs
        and high commercial search volume.
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured. Add it to .env or environment.")

        prompt = f"""
You are Helia-Radar, Director Helia's Market Intelligence and Opportunity Discovery Agent at HeliaTech Media.
Identify {count} high-growth B2B SaaS software tools {"in the category: " + category if category else "across high-margin B2B niches"}.

Target criteria:
1. High commercial buyer intent (people searching for pricing, reviews, and alternatives).
2. Well-known for having a lucrative affiliate or partner program (e.g. via Rewardful, PartnerStack, FirstPromoter, Impact).
3. Subscription-based model ($20 - $200+/month) enabling recurring commissions.

Provide the output strictly conforming to the requested schema.
"""

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

        try:
            data = json.loads(response.text)
            return [RadarKeyword(**item) for item in data]
        except Exception as e:
            print(f"Error parsing radar response: {e}")
            return []
