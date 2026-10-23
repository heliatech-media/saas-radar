"""
Helia-VersusEngine: High-Converting B2B SaaS Head-to-Head Duel & Comparison Agent.
Produces forensic 'Tool A vs Tool B' masterclasses with side-by-side matrices,
empirical scaling economics, and dual-affiliate monetization links.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-VersusEngine] %(message)s")
logger = logging.getLogger("Helia-VersusEngine")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from agents.config import GEMINI_API_KEY, GEMINI_MODEL, BLOG_CONTENT_DIR, DATA_DIR
from agents.image_generator_agent import ImageGeneratorAgent

# High-intent B2B rivalry pairs with enormous Google search volume & high buyer intent
HIGH_INTENT_DUELS = [
    {
        "tool_a": "make",
        "tool_b": "zapier",
        "category": "Automation & No-Code",
        "duel_title": "Make vs Zapier: The 2026 Enterprise Automation Teardown",
        "focus": "Visual nodal canvas vs sequential zaps, pricing per 10k operations, complex JSON parsing"
    },
    {
        "tool_a": "elevenlabs",
        "tool_b": "heygen",
        "category": "AI Voice & Video Infrastructure",
        "duel_title": "ElevenLabs vs HeyGen: Voice Synthesis vs AI Avatar Dominance",
        "focus": "Voice cloning inflection vs photorealistic video avatars, latency, enterprise API licensing"
    },
    {
        "tool_a": "apollo-io",
        "tool_b": "lusha",
        "category": "B2B Sales & Lead Intelligence",
        "duel_title": "Apollo.io vs Lusha: Direct Phone & Email Enrichment Battle",
        "focus": "Database accuracy, GDPR/CCPA enterprise compliance, sequencing automation vs Chrome extension"
    },
    {
        "tool_a": "clickup",
        "tool_b": "monday-com",
        "category": "Work OS & Project Management",
        "duel_title": "ClickUp vs Monday.com: The Definitive Enterprise Project OS Shootout",
        "focus": "All-in-one feature density vs intuitive visual boards, performance at 500+ users, pricing tiers"
    },
    {
        "tool_a": "beehiiv",
        "tool_b": "brevo",
        "category": "Marketing & Newsletter Infrastructure",
        "duel_title": "Beehiiv vs Brevo: Newsletter Monetization vs Multi-Channel CRM",
        "focus": "Ad network & recommendation boost vs transactional SMTP, SMS, and marketing automation"
    },
    {
        "tool_a": "supabase",
        "tool_b": "retool",
        "category": "DevTools & Internal Tooling",
        "duel_title": "Supabase vs Retool: Open-Source Backend vs Rapid Internal App Builder",
        "focus": "PostgreSQL with row-level security vs drag-and-drop frontend CRUD canvas"
    }
]


class VersusAgent:
    """
    Autonomous 'Tool A vs Tool B' Comparison Architect.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        self.artist = ImageGeneratorAgent(api_key=self.api_key)

    def generate_versus_article(self, duel_config: Dict) -> Optional[Path]:
        """
        Synthesizes an exhaustive, objective, high-converting head-to-head comparison article.
        """
        if not self.client:
            logger.error("Gemini API client not initialized.")
            return None

        slug_a = duel_config["tool_a"]
        slug_b = duel_config["tool_b"]
        category = duel_config["category"]
        duel_slug = f"{slug_a}-vs-{slug_b}"
        target_file = BLOG_CONTENT_DIR / f"{duel_slug}.md"

        if target_file.exists():
            logger.info(f"Versus article '{duel_slug}' already exists. Skipping generation.")
            return target_file

        logger.info(f"Architecting deep forensic versus showdown: '{slug_a.upper()} vs {slug_b.upper()}'...")

        prompt = f"""
You are Helia, Chief Operating Officer & Senior Systems Architect at HeliaTech Media (heliatech.online).
Author a definitive, comprehensive, empirical 2,500-word B2B comparison masterclass:
Duel: "{duel_config['duel_title']}"
Tool A: {slug_a.title()} (Affiliate Hop: /go/{slug_a})
Tool B: {slug_b.title()} (Affiliate Hop: /go/{slug_b})
Category: {category}
Focus Areas: {duel_config['focus']}

Requirements:
1. Style: Authoritative, forensic, direct, technical, and objective. Zero generic promotional fluff.
2. Structure:
   - Executive Verdict (The 30-Second Summary: who should buy Tool A vs Tool B)
   - Comprehensive Side-by-Side Comparison Matrix (Markdown table with 8+ empirical criteria: Core Architecture, Pricing at Scale, Learning Curve, API & Webhooks, Ecosystem, Security, Best For)
   - Round 1: Architecture & Workflow Paradigms (Technical Teardown)
   - Round 2: Total Cost of Ownership & Scaling Math (Real calculations comparing costs at 5k, 50k, and 500k monthly operations/users)
   - Round 3: Integration Depth & Developer Ergonomics
   - Round 4: Critical Bottlenecks & Where Each Platform Fails
   - Concrete Real-World Decision Framework:
     * When to strictly choose {slug_a.title()}
     * When to strictly choose {slug_b.title()}
   - Official Evaluation CTAs for BOTH platforms using their respective /go/{slug_a} and /go/{slug_b} hops.
3. Metadata Frontmatter (YAML):
---
title: "{duel_config['duel_title']}"
description: "Comprehensive 2026 head-to-head teardown of {slug_a.title()} vs {slug_b.title()}. Empirical comparison matrix, pricing scaling math, architectural benchmarks, and executive recommendations."
date: "2026-10-23"
author: "HELIA TECH"
category: "{category}"
tags:
  - {slug_a.title()}
  - {slug_b.title()}
  - "{slug_a.title()} vs {slug_b.title()}"
  - Comparison
  - B2B Software
readingTime: "12 MIN"
tool_slug: "{slug_a}"
tldr:
  - "{slug_a.title()} excels at [specific superpower], delivering unmatched leverage for [target persona]."
  - "{slug_b.title()} remains superior for [alternative superpower], providing an edge when [condition]."
  - "Economic scaling breakdown reveals up to 70% cost variation between both platforms at scale."
---

Write the complete markdown article without truncation.
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                )
            )
            content = response.text.strip()
            
            # Clean markdown codeblocks if wrapped
            if content.startswith("```markdown"):
                content = content[11:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            target_file.write_text(content, encoding="utf-8")
            logger.info(f"✅ Published versus masterclass: {target_file.name}")

            # Generate custom duel artwork
            self.generate_duel_visual(slug_a, slug_b, duel_slug)

            return target_file

        except Exception as e:
            logger.error(f"Error generating versus article {duel_slug}: {e}")
            return None

    def generate_duel_visual(self, slug_a: str, slug_b: str, duel_slug: str):
        """Generates a dedicated 1200x630 duel artwork for the versus post."""
        visual_dir = ROOT_DIR / "site" / "public" / "images" / "blog"
        visual_dir.mkdir(parents=True, exist_ok=True)
        svg_path = visual_dir / f"{duel_slug}.svg"
        png_path = visual_dir / f"{duel_slug}.png"

        name_a = slug_a.replace("-", " ").title()
        name_b = slug_b.replace("-", " ").title()

        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="50%" stop-color="#030712"/>
      <stop offset="100%" stop-color="#0b0f19"/>
    </linearGradient>
    <linearGradient id="glow-a" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#06b6d4" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="glow-b" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#f59e0b" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.7" stroke-opacity="0.4"/>
    </pattern>
  </defs>

  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#grid)"/>

  <!-- Side Light Pillars -->
  <circle cx="200" cy="315" r="280" fill="url(#glow-a)"/>
  <circle cx="1000" cy="315" r="280" fill="url(#glow-b)"/>

  <!-- Divider Line -->
  <line x1="600" y1="80" x2="600" y2="550" stroke="#334155" stroke-width="2" stroke-dasharray="6,6"/>

  <!-- VS Center Badge -->
  <circle cx="600" cy="315" r="48" fill="#0f172a" stroke="#06b6d4" stroke-width="2.5"/>
  <text x="600" y="324" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="24" font-weight="900" fill="#f8fafc" text-anchor="middle" letter-spacing="2">VS</text>

  <!-- Side A -->
  <g transform="translate(140, 240)">
    <rect x="0" y="0" width="360" height="150" rx="20" fill="#0b1329" fill-opacity="0.8" stroke="#06b6d4" stroke-width="1.5"/>
    <text x="180" y="65" font-family="'Plus Jakarta Sans', sans-serif" font-size="34" font-weight="900" fill="#ffffff" text-anchor="middle">{name_a}</text>
    <text x="180" y="105" font-family="'JetBrains Mono', monospace" font-size="14" font-weight="600" fill="#38bdf8" text-anchor="middle">EMPIRICAL BENCHMARK</text>
  </g>

  <!-- Side B -->
  <g transform="translate(700, 240)">
    <rect x="0" y="0" width="360" height="150" rx="20" fill="#1c1608" fill-opacity="0.8" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="180" y="65" font-family="'Plus Jakarta Sans', sans-serif" font-size="34" font-weight="900" fill="#ffffff" text-anchor="middle">{name_b}</text>
    <text x="180" y="105" font-family="'JetBrains Mono', monospace" font-size="14" font-weight="600" fill="#fbbf24" text-anchor="middle">FORENSIC TEARDOWN</text>
  </g>

  <!-- Top Header -->
  <g transform="translate(600, 80)">
    <text x="0" y="0" font-family="'Plus Jakarta Sans', sans-serif" font-size="14" font-weight="800" fill="#06b6d4" text-anchor="middle" letter-spacing="4">HELIA TECH HEAD-TO-HEAD DUEL MATRIX</text>
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
                logger.info(f"✅ Duel visual rasterized: {png_path.name}")
        except Exception as e:
            logger.warning(f"Could not rasterize duel PNG: {e}")

    def execute_versus_sweep(self, limit: int = 1) -> List[Path]:
        """Runs the versus agent on top candidate duels."""
        generated = []
        for duel in HIGH_INTENT_DUELS:
            if len(generated) >= limit:
                break
            art_path = self.generate_versus_article(duel)
            if art_path:
                generated.append(art_path)
        return generated


if __name__ == "__main__":
    agent = VersusAgent()
    results = agent.execute_versus_sweep(limit=1)
    print(f"\n--- Helia-VersusEngine Results ---")
    print(f"Generated {len(results)} Versus Masterclasses.")
    for r in results:
        print(f" • {r.name}")
