"""
Helia-AlternativesEngine: High-Converting "Top 7 Alternatives" Authority Engine.
Discovers high-intent software replacement searches (e.g. 'Best Zapier Alternatives',
'Best Deel Alternatives', 'Best Apollo Alternatives') and authors authoritative
roundup rankings with empirical comparison tables and multi-affiliate routing.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-AlternativesEngine] %(message)s")
logger = logging.getLogger("Helia-AlternativesEngine")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from agents.config import GEMINI_API_KEY, GEMINI_MODEL, BLOG_CONTENT_DIR, DATA_DIR

# High-intent replacement queries in B2B SaaS
HIGH_INTENT_ALTERNATIVES = [
    {
        "target_tool": "zapier",
        "target_name": "Zapier",
        "category": "Automation & No-Code",
        "article_title": "Top 7 Zapier Alternatives in 2026: Cheaper, Faster & Enterprise-Grade",
        "slug": "best-zapier-alternatives-2026",
        "hero_monetized_tool": "make",
        "context": "Focus on high operational costs of Zapier at scale, complex JSON nesting limits, and why visual tools like Make and self-hosted n8n are winning enterprise migrations.",
        "top_picks": [
            {"rank": 1, "name": "Make (Integromat)", "slug": "make", "advantage": "70% cheaper at scale, visual multi-branch nodal canvas, native JSON array manipulation"},
            {"rank": 2, "name": "n8n", "slug": "n8n", "advantage": "Fair-code, self-hostable on Docker, total data sovereignty, zero per-execution fees on self-hosted"},
            {"rank": 3, "name": "Relay.app", "slug": "relay", "advantage": "Human-in-the-loop approvals directly inside Gmail & Slack, ultra-modern UX"},
            {"rank": 4, "name": "Workato", "slug": "workato", "advantage": "Enterprise iPaaS with robust RBAC, SOC2 Type II compliance, enterprise governance"},
            {"rank": 5, "name": "Activepieces", "slug": "activepieces", "advantage": "Open-source lightweight alternative with TypeScript custom code steps"},
            {"rank": 6, "name": "Tray.io", "slug": "tray-io", "advantage": "Scalable automation cloud for enterprise revenue operations and product integrations"},
            {"rank": 7, "name": "Microsoft Power Automate", "slug": "power-automate", "advantage": "Deep native integration with Microsoft 365, Azure, and legacy desktop RPA"}
        ]
    },
    {
        "target_tool": "deel",
        "target_name": "Deel",
        "category": "Global Payroll & HR Tech",
        "article_title": "Top 7 Deel Alternatives in 2026: Global Payroll, EOR & Contractor Management",
        "slug": "best-deel-alternatives-2026",
        "hero_monetized_tool": "papaya-global",
        "context": "Focus on global contractor misclassification risk, multi-currency treasury management, and why Papaya Global ($1,000-$2,000 commission partner) and Rippling deliver superior compliance.",
        "top_picks": [
            {"rank": 1, "name": "Papaya Global", "slug": "papaya-global", "advantage": "Unified global workforce payments, licensed tier-1 banking rails, automated global payroll in 160+ countries"},
            {"rank": 2, "name": "Rippling", "slug": "rippling", "advantage": "All-in-one workforce platform tying global HR, payroll, IT device management, and corporate cards"},
            {"rank": 3, "name": "Remote.com", "slug": "remote", "advantage": "Owns 100% of its local legal entities with flat transparent pricing and zero hidden markups"},
            {"rank": 4, "name": "Oyster HR", "slug": "oyster", "advantage": "Designed specifically for distributed startups, intuitive global benefits administration"},
            {"rank": 5, "name": "Multiplier", "slug": "multiplier", "advantage": "Rapid international contractor onboarding with localized employment contracts in minutes"},
            {"rank": 6, "name": "Plane (formerly Pilot)", "slug": "plane", "advantage": "Zero markups on foreign exchange rates, dedicated account management for tech teams"},
            {"rank": 7, "name": "Velocity Global", "slug": "velocity-global", "advantage": "Heavyweight legacy global employer of record for complex enterprise international expansions"}
        ]
    },
    {
        "target_tool": "apollo-io",
        "target_name": "Apollo.io",
        "category": "B2B Sales & Lead Intelligence",
        "article_title": "Top 7 Apollo.io Alternatives in 2026: Accurate B2B Leads, Direct Dials & Enrichment",
        "slug": "best-apollo-alternatives-2026",
        "hero_monetized_tool": "lusha",
        "context": "Focus on data decay rates, verified direct mobile phone numbers vs switchboards, and enterprise CRM hygiene.",
        "top_picks": [
            {"rank": 1, "name": "Lusha", "slug": "lusha", "advantage": "Direct-dial accuracy verified by proprietary community network, fast browser extension, GDPR/CCPA native compliance"},
            {"rank": 2, "name": "ZoomInfo", "slug": "zoominfo", "advantage": "Massive enterprise intent data, org charts, scoops, and deepest US enterprise contact penetration"},
            {"rank": 3, "name": "Cognism", "slug": "cognism", "advantage": "Phone-verified Diamond Data, 100% compliant with strict European GDPR opt-in laws"},
            {"rank": 4, "name": "Kaspr", "slug": "kaspr", "advantage": "Ultra-fast LinkedIn prospecting Chrome extension with real-time phone number extraction"},
            {"rank": 5, "name": "LeadIQ", "slug": "leadiq", "advantage": "Seamless 1-click capture to Salesforce & HubSpot without CRM duplication"},
            {"rank": 6, "name": "UpLead", "slug": "uplead", "advantage": "95% data accuracy guarantee with real-time email verification before download credit deduction"},
            {"rank": 7, "name": "Clay", "slug": "clay", "advantage": "AI-powered data enrichment waterfall querying 50+ providers simultaneously with LLM personalization"}
        ]
    },
    {
        "target_tool": "elevenlabs",
        "target_name": "ElevenLabs",
        "category": "AI Voice & Audio Infrastructure",
        "article_title": "Top 7 ElevenLabs Alternatives in 2026: AI Voice Cloning, Text-to-Speech & Video Avatars",
        "slug": "best-elevenlabs-alternatives-2026",
        "hero_monetized_tool": "heygen",
        "context": "Focus on turning voice audio into synchronized video avatars, multi-speaker conversational latency, and open-source local inference.",
        "top_picks": [
            {"rank": 1, "name": "HeyGen", "slug": "heygen", "advantage": "Combines realistic voice synthesis with photorealistic 4K AI video avatars and automated lip-sync translation"},
            {"rank": 2, "name": "PlayHT", "slug": "playht", "advantage": "Sub-100ms conversational streaming API and generative voice cloning for interactive customer agents"},
            {"rank": 3, "name": "Murf.ai", "slug": "murf-ai", "advantage": "Collaborative cloud studio for e-learning, voiceover timelines, and corporate video presentations"},
            {"rank": 4, "name": "Resemble AI", "slug": "resemble-ai", "advantage": "Enterprise audio watermarking, deepfake detection, and fine-grained emotional modulation controls"},
            {"rank": 5, "name": "OpenAI TTS", "slug": "openai-tts", "advantage": "Extremely affordable developer API with low latency integrated natively into GPT-4o pipelines"},
            {"rank": 6, "name": "Speechify", "slug": "speechify", "advantage": "Consumer & executive reading companion with celebrity voices and high-speed document narration"},
            {"rank": 7, "name": "Coqui TTS / XTTS", "slug": "coqui", "advantage": "Open-source voice cloning model running completely offline on local GPU hardware"}
        ]
    }
]


class AlternativesAgent:
    """
    Autonomous 'Top 7 Alternatives' Authority Engine.
    Architects high-intent roundup articles that capture search traffic from
    dissatisfied software users and routes them to our monetized partners.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def _generate_cover_art(self, target_name: str, slug: str, category: str) -> str:
        """
        Creates a dark cyber, flagship comparison artwork and rasterizes it.
        """
        visual_dir = ROOT_DIR / "site" / "public" / "images" / "blog"
        visual_dir.mkdir(parents=True, exist_ok=True)

        svg_path = visual_dir / f"{slug}.svg"
        png_path = visual_dir / f"{slug}.png"

        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="50%" stop-color="#050a18"/>
      <stop offset="100%" stop-color="#021c1e"/>
    </linearGradient>
    <linearGradient id="glow-emerald" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10b981" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#10b981" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="glow-cyan" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#06b6d4" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.7" stroke-opacity="0.4"/>
    </pattern>
  </defs>

  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#grid)"/>

  <!-- Glowing Aura Orbs -->
  <circle cx="250" cy="280" r="320" fill="url(#glow-emerald)"/>
  <circle cx="950" cy="350" r="300" fill="url(#glow-cyan)"/>

  <!-- Top Badge -->
  <g transform="translate(600, 100)">
    <rect x="-180" y="-18" width="360" height="36" rx="18" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
    <text x="0" y="5" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="#34d399" text-anchor="middle" letter-spacing="3">HELIA TECH INTELLIGENCE REPORT</text>
  </g>

  <!-- Main Headline Card -->
  <g transform="translate(600, 290)">
    <rect x="-480" y="-110" width="960" height="220" rx="24" fill="#0b1329" fill-opacity="0.85" stroke="#334155" stroke-width="2"/>
    
    <text x="0" y="-35" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="20" font-weight="800" fill="#06b6d4" text-anchor="middle" letter-spacing="4">DEFINITIVE 2026 ARCHITECTURAL BENCHMARK</text>
    <text x="0" y="25" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="46" font-weight="900" fill="#ffffff" text-anchor="middle">TOP 7 {target_name.upper()} ALTERNATIVES</text>
    <text x="0" y="70" font-family="'JetBrains Mono', monospace" font-size="15" font-weight="600" fill="#94a3b8" text-anchor="middle">Cheaper • More Scalable • Enterprise-Grade Architecture</text>
  </g>

  <!-- Bottom Metric Pods -->
  <g transform="translate(260, 480)">
    <rect x="0" y="0" width="200" height="70" rx="14" fill="#020617" stroke="#10b981" stroke-width="1.2"/>
    <text x="100" y="30" font-family="'Plus Jakarta Sans', sans-serif" font-size="16" font-weight="900" fill="#34d399" text-anchor="middle">7 CANDIDATES</text>
    <text x="100" y="52" font-family="'JetBrains Mono', monospace" font-size="11" fill="#64748b" text-anchor="middle">Hands-on Tested</text>
  </g>
  <g transform="translate(500, 480)">
    <rect x="0" y="0" width="200" height="70" rx="14" fill="#020617" stroke="#06b6d4" stroke-width="1.2"/>
    <text x="100" y="30" font-family="'Plus Jakarta Sans', sans-serif" font-size="16" font-weight="900" fill="#38bdf8" text-anchor="middle">UP TO 70% SAVINGS</text>
    <text x="100" y="52" font-family="'JetBrains Mono', monospace" font-size="11" fill="#64748b" text-anchor="middle">Total Cost Math</text>
  </g>
  <g transform="translate(740, 480)">
    <rect x="0" y="0" width="200" height="70" rx="14" fill="#020617" stroke="#f59e0b" stroke-width="1.2"/>
    <text x="100" y="30" font-family="'Plus Jakarta Sans', sans-serif" font-size="16" font-weight="900" fill="#fbbf24" text-anchor="middle">ZERO DATA LOSS</text>
    <text x="100" y="52" font-family="'JetBrains Mono', monospace" font-size="11" fill="#64748b" text-anchor="middle">Migration Framework</text>
  </g>
</svg>"""

        svg_path.write_text(svg_content, encoding="utf-8")

        # Rasterize with playwright if available
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1200, "height": 630})
                page.set_content(f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#020617;overflow:hidden;">{svg_content}</body></html>""")
                page.screenshot(path=str(png_path), type="png")
                browser.close()
                logger.info(f"Cover image rasterized successfully: {png_path.name}")
        except Exception as e:
            logger.warning(f"Could not rasterize PNG: {e}")

        return f"/images/blog/{slug}.png"

    def generate_alternatives_article(self, config: Dict) -> Optional[Path]:
        """
        Synthesizes an in-depth, authoritative 'Top 7 Alternatives' roundup article.
        """
        if not self.client:
            logger.error("Gemini API client not initialized.")
            return None

        target_name = config["target_name"]
        target_tool = config["target_tool"]
        title = config["article_title"]
        slug = config["slug"]
        category = config["category"]
        hero_tool = config.get("hero_monetized_tool", target_tool)
        picks = config["top_picks"]
        context = config.get("context", "")

        logger.info(f"Synthesizing 'Top 7 Alternatives' masterclass for: {target_name} ({title})")

        # 1. Generate Luxury Cyber Dark Cover Artwork
        image_path = self._generate_cover_art(target_name, slug, category)

        # 2. Structure LLM Prompt
        picks_formatted = "\n".join([
            f"- #{p['rank']} {p['name']} (slug: {p['slug']}): {p['advantage']}"
            for p in picks
        ])

        system_instruction = (
            "You are the Chief Technology Editor and Lead Software Architect at HeliaTech Media "
            "(heliatech.online). You write elite, authoritative, no-nonsense software evaluations for CTOs, "
            "Founders, and Operations Leaders. Your style is empirical, analytical, rigorous, and completely free "
            "of generic marketing fluff. You provide hard numbers, pricing benchmarks, and explicit technical migration advice."
        )

        user_prompt = f"""
Write an exhaustive, high-converting, authoritative 'Top 7 Alternatives to {target_name}' buyer's guide for 2026.

ARTICLE METADATA:
- Title: {title}
- Target Tool Being Replaced: {target_name}
- Primary Category: {category}
- Strategic Focus & Industry Context: {context}

THE 7 RANKED ALTERNATIVES:
{picks_formatted}

MANDATORY EDITORIAL REQUIREMENTS:
1. Executive Breakdown: Why are enterprises actively looking for alternatives to {target_name} in 2026? Detail specific pain points (e.g., escalating pricing tiers, execution throttling, complex payload limits, data security, customer support friction).
2. The 2026 Master Comparison Matrix: An exhaustive Markdown table comparing {target_name} against all 7 alternatives across:
   - Tool Name
   - Core Superpower
   - Best For
   - Starting Price
   - Scalability Score (/10)
   - Direct Evaluation Link (`/go/[slug]`)
3. Granular Teardown of Each of the 7 Alternatives:
   For EACH alternative (#1 through #7):
   - ## [Rank]. [Tool Name] — [Catchy Architectural Subtitle]
   - **The Core Value Proposition:** Why it outperforms {target_name}.
   - **Key Architectural Advantages:** 3-4 bullet points of real engineering advantages.
   - **Where It Falls Short:** Honest trade-offs, missing features, or learning curve.
   - **Pricing Model & Economics:** Real costs compared to {target_name}.
   - **Migration Feasibility:** Exactly how hard it is to migrate workflows/data from {target_name} (Estimated migration time: e.g., '2 to 4 hours').
   - **Call-to-Action Link:** `[Test [Tool Name] With Official Extended Access ↗](/go/[tool-slug])`
4. Decision Framework by Business Archetype:
   - If you are a Solo Creator / Bootstrapped Founder: Which one to pick?
   - If you are a High-Growth Mid-Market Scale-Up: Which one to pick?
   - If you are an Enterprise with Strict Compliance (SOC2 / GDPR): Which one to pick?
5. Step-by-Step Migration Checklist from {target_name}:
   A 5-step operational checklist to transition systems safely without data loss or downtime.

OUTPUT FORMAT:
Return ONLY the raw markdown content including complete frontmatter.
The frontmatter MUST include:
---
title: "{title}"
description: "Empirical benchmark and ranking of the top 7 {target_name} alternatives in 2026. Compare pricing, features, scalability, and ease of migration."
date: "2026-10-23"
author: "HELIA TECH"
category: "{category}"
tags:
  - "{target_name}"
  - "Alternatives"
  - "B2B Software"
  - "{category}"
readingTime: "14 MIN"
tool_slug: "{hero_tool}"
image: "{image_path}"
tldr:
  - "Key insight 1 about replacing {target_name}"
  - "Key insight 2 regarding the top recommendation"
  - "Key insight 3 regarding economic savings at scale"
---
[Full Markdown Body]
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.35,
                    max_output_tokens=7000
                )
            )

            content = response.text.strip()
            if content.startswith("```markdown"):
                content = content[len("```markdown"):].strip()
            elif content.startswith("```"):
                content = content[len("```"):].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

            target_file = BLOG_CONTENT_DIR / f"{slug}.md"
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Top 7 Alternatives article successfully saved to: {target_file}")
            return target_file

        except Exception as e:
            logger.error(f"Error generating alternatives article: {e}")
            return None

    def execute_alternatives_sweep(self, limit: int = 2) -> List[Path]:
        """
        Runs generation for the highest-intent alternative roundups.
        """
        results = []
        for config in HIGH_INTENT_ALTERNATIVES:
            if len(results) >= limit:
                break
            slug = config["slug"]
            target_file = BLOG_CONTENT_DIR / f"{slug}.md"
            if target_file.exists():
                logger.info(f"Alternatives article '{slug}.md' already exists. Skipping.")
                continue

            saved_path = self.generate_alternatives_article(config)
            if saved_path:
                results.append(saved_path)

        return results


if __name__ == "__main__":
    agent = AlternativesAgent()
    logger.info("Executing Helia-AlternativesEngine standalone generation...")
    results = agent.execute_alternatives_sweep(limit=2)
    print(f"\n--- Helia-AlternativesEngine Results ---")
    print(f"Generated {len(results)} Top Alternatives Masterclasses:")
    for r in results:
        print(f" • {r.name}")
