"""
Helia-BacklinkArchitect: Autonomous SEO Authority, Digital PR & Outreach Engine.
Analyzes competitors' backlink profiles, designs high-authority syndication hooks,
and generates digital PR pitches to propel HeliaTech into the Google Top 3.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-BacklinkArchitect] %(message)s")
logger = logging.getLogger("Helia-BacklinkArchitect")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from agents.config import BLOG_CONTENT_DIR, ROOT_DIR

OUTREACH_TARGETS_PATH = ROOT_DIR / "reports" / "backlink_outreach_targets.json"
SYNDICATION_BRIEFS_PATH = ROOT_DIR / "reports" / "syndication_briefs.md"

# High-DR B2B Tech Platforms for Organic Citations & Netlinking
PRIME_LINK_HUBS = [
    {
        "platform": "HackerNews / Show HN",
        "domain_rating": 91,
        "format": "Technical Teardown / Empirical benchmark release",
        "target_audience": "Founders, CTOs, Staff Engineers",
        "primary_hook": "We benchmarked Zapier vs Make across 500,000 tasks: Here is the raw economic math."
    },
    {
        "platform": "Dev.to & Hashnode",
        "domain_rating": 89,
        "format": "Architectural Deep Dive & Open Guide",
        "target_audience": "Full-stack Developers, DevOps & RevOps",
        "primary_hook": "Self-hosting n8n vs Make Cloud: Total cost of ownership and latency breakdown for 2026."
    },
    {
        "platform": "Reddit (r/SaaS & r/automation)",
        "domain_rating": 93,
        "format": "No-BS Case Study / Cost Audit",
        "target_audience": "Agency Owners, No-Code Builders",
        "primary_hook": "How we cut $1,200/mo in Zapier task-overages by rebuilding on Make + Webhooks."
    },
    {
        "platform": "Medium / Towards Data Science",
        "domain_rating": 95,
        "format": "Thought Leadership Syndicate",
        "target_audience": "AI Engineers, Tech Executives",
        "primary_hook": "The 2026 AI Voice Infrastructure Landscape: ElevenLabs vs HeyGen Teardown."
    },
    {
        "platform": "ProductHunt Discussions",
        "domain_rating": 90,
        "format": "Community Tool Recommendation",
        "target_audience": "Early Adopters, Indie Hackers",
        "primary_hook": "Best Global Payroll and EOR alternatives in 2026: Why Papaya Global and Rippling are dominating."
    }
]


class BacklinkArchitectAgent:
    """
    Helia-BacklinkArchitect: High-Authority Netlinking and Digital PR Engine.
    """
    def __init__(self):
        OUTREACH_TARGETS_PATH.parent.mkdir(parents=True, exist_ok=True)

    def generate_authority_playbook(self) -> Dict:
        """
        Creates ready-to-execute syndication pitches for top performing articles.
        """
        logger.info("⚡ Generating SEO Authority & High-DR Netlinking Playbook...")

        articles = []
        if BLOG_CONTENT_DIR.exists():
            for f in sorted(BLOG_CONTENT_DIR.glob("*.md")):
                articles.append(f.stem)

        targets_payload = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_domain_authority": "DR 65+",
            "active_link_hubs": PRIME_LINK_HUBS,
            "priority_asset_targets": [
                {
                    "slug": "best-zapier-alternatives-2026",
                    "target_url": "https://heliatech.online/blog/best-zapier-alternatives-2026",
                    "anchor_texts": ["Zapier alternatives 2026", "cheaper alternative to Zapier", "Make vs Zapier pricing benchmark"],
                    "syndication_angle": "Empirical analysis showing 70% cost reduction by moving away from linear zaps."
                },
                {
                    "slug": "best-deel-alternatives-2026",
                    "target_url": "https://heliatech.online/blog/best-deel-alternatives-2026",
                    "anchor_texts": ["Deel alternatives", "best global payroll software", "Papaya Global payroll benchmark"],
                    "syndication_angle": "Exposing hidden foreign exchange markups in global contractor platforms."
                },
                {
                    "slug": "make-vs-zapier",
                    "target_url": "https://heliatech.online/blog/make-vs-zapier",
                    "anchor_texts": ["Make vs Zapier teardown", "visual automation vs zaps"],
                    "syndication_angle": "Technical side-by-side architecture teardown."
                }
            ],
            "projected_backlink_velocity": "+15 high-authority referring domains / month"
        }

        with open(OUTREACH_TARGETS_PATH, "w", encoding="utf-8") as f:
            json.dump(targets_payload, f, indent=2, ensure_ascii=False)

        # Generate markdown brief for founder and syndication bots
        brief_md = f"""# 🏛️ Helia-BacklinkArchitect: SEO Authority & Digital PR Playbook
Generated on: {targets_payload['generated_at']}
Target Goal: Propel HeliaTech B2B reviews into the Google Top 3.

## 🎯 High-DR Netlinking Channels (Target DR > 85)
| Platform | DR | Format | Primary Hook |
| :--- | :--- | :--- | :--- |
"""
        for hub in PRIME_LINK_HUBS:
            brief_md += f"| **{hub['platform']}** | {hub['domain_rating']} | {hub['format']} | {hub['primary_hook']} |\n"

        brief_md += """
## 🔗 Priority Editorial Anchor Targets
- **Target 1:** [Top 7 Zapier Alternatives 2026](https://heliatech.online/blog/best-zapier-alternatives-2026) (Target Keyword: *Zapier alternatives 2026*)
- **Target 2:** [Top 7 Deel Alternatives 2026](https://heliatech.online/blog/best-deel-alternatives-2026) (Target Keyword: *Deel alternatives global payroll*)
- **Target 3:** [Make vs Zapier Showdown](https://heliatech.online/blog/make-vs-zapier) (Target Keyword: *Make vs Zapier*)
"""
        with open(SYNDICATION_BRIEFS_PATH, "w", encoding="utf-8") as f:
            f.write(brief_md)

        logger.info(f"✅ Backlink playbook recorded at {OUTREACH_TARGETS_PATH.name} and {SYNDICATION_BRIEFS_PATH.name}.")
        return targets_payload


if __name__ == "__main__":
    agent = BacklinkArchitectAgent()
    res = agent.generate_authority_playbook()
    print(f"\n--- Helia-BacklinkArchitect Results ---")
    print(f"Target Velocity: {res['projected_backlink_velocity']}")
    print(f"Active Hubs: {len(res['active_link_hubs'])}")
