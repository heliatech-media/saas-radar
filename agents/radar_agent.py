"""
Agent 1: Market & Intent Radar (Senior Discovery Specialist).
Identifies high-converting SaaS products, search intents, and recurring affiliate opportunities.
Actively sniffs and prioritizes Rewardful and Stripe-powered viral SaaS ecosystems.
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import List, Optional

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from google import genai
from google.genai import types
from agents.config import GEMINI_API_KEY, GEMINI_MODEL, TARGET_NICHES, call_gemini_with_failover
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
        and high commercial search volume, strictly prioritizing the Rewardful & Stripe ecosystem.
        """
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured. Add it to .env or environment.")

        existing = self.get_existing_tool_slugs()
        exclude_str = ", ".join(existing) if existing else "none"

        prompt = f"""
You are Helia-Radar, Chief Market Intelligence and Opportunity Discovery Agent at HeliaTech Media.
Identify {count} high-growth, high-converting B2B & Creator SaaS tools {"in category: " + category if category else "across high-margin B2B SaaS niches (AI Video, Audio/Podcasting, DevTools, Newsletters, Automation)"}.

CRITICAL MANDATES:
1. High commercial buyer intent (users searching for pricing, reviews, teardowns, and alternatives).
2. HIGH PRIORITY: Actively discover software utilizing REWARDFUL (Stripe Billing affiliate ecosystem, e.g. Castmagic, Transistor, Riverside, Podia, Memberstack, Beehiiv, VEED, Submagic) or PartnerStack/FirstPromoter with 20% to 50% recurring MRR.
   - Note: HeliaTech holds an instant pre-approved Rewardful token ('heliatech') universally accepted via '?via=heliatech'. Prioritizing Rewardful SaaS delivers instant, zero-delay monetization.
3. DO NOT include any of the following software tools because they have ALREADY been evaluated:
[{exclude_str}]
4. Focus on breakout, viral modern platforms with strong organic search velocity (e.g. Supabase, Vercel, Framer, Typeform, Linear, Apollo.io, PhantomBuster, Beehiiv, Lemlist, Lovable, v0, Castmagic).

Provide the output strictly conforming to the requested JSON schema.
"""

        try:
            response = call_gemini_with_failover(
                client=self.client,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema={
                        "type": "ARRAY",
                        "items": RadarKeyword.model_json_schema(),
                    },
                    temperature=0.7,
                ),
                preferred_model=self.model
            )
        except Exception as e:
            print(f"[Helia-Radar] ⚠️ Gemini discovery offline ({e}). Falling back to seed catalog.")
            return []

        try:
            data = json.loads(response.text)
            keywords = [RadarKeyword(**item) for item in data]
            print(f"[Helia-Radar] 🛰️ Successfully discovered {len(keywords)} new candidate tools: {[k.tool_name for k in keywords]}")
            return keywords
        except Exception as e:
            print(f"[Helia-Radar] ❌ Error parsing radar response: {e}")
            return []

    def verify_rewardful_compatibility(self, domain_url: str) -> bool:
        """Sniffs live HTML to verify if candidate runs Rewardful (r.wdfl.co)."""
        try:
            from agents.rewardful_engine_agent import RewardfulEngineAgent
            engine = RewardfulEngineAgent()
            return engine.detect_rewardful_fingerprint(domain_url)
        except Exception:
            return False

    def scout_trending_software(self) -> RadarKeyword:
        """
        Discovers a single high-potential trending tool, actively sniffing for Rewardful compatibility
        and prioritizing breakout high-converting software.
        Guarantees that the selected tool is NEVER already indexed in local reviews.
        """
        existing = set(self.get_existing_tool_slugs())
        opps = self.discover_trending_opportunities(count=5)
        
        valid_opps = []
        for opp in opps:
            slug = re.sub(r'[^a-z0-9]+', '-', opp.tool_name.lower()).strip('-')
            if slug not in existing:
                valid_opps.append(opp)
            else:
                print(f"[Helia-Radar] ⏩ Candidate '{opp.tool_name}' ({slug}) already indexed in reviews. Skipping.")

        if valid_opps:
            for opp in valid_opps:
                if "rewardful" in opp.average_commission.lower() or "stripe" in opp.average_commission.lower() or "recurring" in opp.average_commission.lower():
                    print(f"[Helia-Radar] 💎 Priority candidate selected: {opp.tool_name} (Rewardful/Stripe recurring target)")
                    return opp
            return valid_opps[0]

        for seed in self.get_seed_tools():
            slug = re.sub(r'[^a-z0-9]+', '-', seed['name'].lower()).strip('-')
            if slug not in existing:
                print(f"[Helia-Radar] 🎯 Seed candidate selected from ecosystem: {seed['name']} ({seed['category']})")
                return RadarKeyword(
                    tool_name=seed["name"],
                    category=seed["category"],
                    search_intent=f"High Commercial ({seed['name']} Review 2026, Pricing, Alternatives)",
                    primary_affiliate_network="Direct / PartnerStack / Rewardful",
                    average_commission=seed["commission"]
                )

        fallback_candidates = [
            {"name": "Clay", "cat": "Data Enrichment & Waterfall B2B Intelligence", "comm": "30% recurring via PartnerStack"},
            {"name": "OpusClip", "cat": "AI Video Repurposing & Shorts Synthesis", "comm": "30% recurring via Rewardful"},
            {"name": "Lovable", "cat": "Full-Stack AI Software Generation & Prototyping", "comm": "25% recurring"},
            {"name": "Runway", "cat": "Generative Video & VFX Foundation Models", "comm": "20% recurring"},
            {"name": "Replicate", "cat": "Cloud AI Model Inference & Serverless GPUs", "comm": "20% recurring"},
        ]
        for fb in fallback_candidates:
            fb_slug = re.sub(r'[^a-z0-9]+', '-', fb['name'].lower()).strip('-')
            if fb_slug not in existing:
                print(f"[Helia-Radar] 🚀 Dynamic breakout fallback selected: {fb['name']}")
                return RadarKeyword(
                    tool_name=fb["name"],
                    category=fb["cat"],
                    search_intent=f"High Commercial ({fb['name']} Review 2026, Pricing, Alternatives)",
                    primary_affiliate_network="Direct / PartnerStack / Rewardful",
                    average_commission=fb["comm"]
                )

        raise RuntimeError("Helia-Radar: All catalog opportunities and seeds are already indexed!")
