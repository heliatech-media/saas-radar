"""
🔭 HELIA VISIONARY STRATEGIST & GROWTH SUPERVISOR
The Master Planning Core for HeliaTech Media:
- Supervises Visitor Velocity & Milestones (Phase 1: 100,000 / mo ➔ Phase 2: 1,000,000 / mo).
- Conducts Algorithmic SaaS Niche Gap & EPC (Earnings Per Click) Yield Analysis.
- Dispatches Strategic Expansion Directives to ContentFactory & SocialGrowth sub-agents.
- Generates Executive Growth Forecasts & Feeds the /sentinel/ Supervision Console.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT_DIR / "site"
CONTENT_DIR = SITE_DIR / "src" / "content"
REPORTS_DIR = ROOT_DIR / "reports"
DATA_DIR = SITE_DIR / "src" / "data"

class VisionaryGrowthAgent:
    def __init__(self):
        self.reviews_dir = CONTENT_DIR / "reviews"
        self.blog_dir = CONTENT_DIR / "blog"
        self.reports_dir = REPORTS_DIR
        self.data_dir = DATA_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Strategic Blueprint Targets
        self.target_phase1_visitors = 100_000
        self.target_phase2_visitors = 1_000_000
        self.avg_monthly_visits_per_ranking_asset = 2_200  # Conservative SEO estimate per comprehensive guide
        self.avg_affiliate_ctr = 0.12  # 12% outbound click rate on deep-dive reviews
        self.avg_affiliate_conversion = 0.035  # 3.5% signup/trial conversion
        self.avg_bounty_royalty = 42.50  # Average blended bounty/recurring payout in USD

    def inspect_current_assets(self) -> Dict[str, Any]:
        """Scans published technical assets and categorizes them."""
        reviews = list(self.reviews_dir.glob("*.md"))
        articles = list(self.blog_dir.glob("*.md"))

        return {
            "reviews_count": len(reviews),
            "articles_count": len(articles),
            "total_indexed_assets": len(reviews) + len(articles),
            "reviews_list": [r.stem for r in reviews],
            "articles_list": [a.stem for a in articles]
        }

    def generate_growth_blueprint(self) -> Dict[str, Any]:
        """Calculates trajectory modeling and selects the next high-yield targets."""
        assets = self.inspect_current_assets()
        total_assets = assets["total_indexed_assets"]

        # Mathematical requirements
        assets_needed_for_100k = int(self.target_phase1_visitors / self.avg_monthly_visits_per_ranking_asset)  # ~46 assets
        assets_needed_for_1m = int(self.target_phase2_visitors / self.avg_monthly_visits_per_ranking_asset)    # ~455 assets

        phase1_progress = min(100.0, round((total_assets / assets_needed_for_100k) * 100, 1))
        phase2_progress = min(100.0, round((total_assets / assets_needed_for_1m) * 100, 2))

        # Financial modeling at 100k visitors
        phase1_hops = int(self.target_phase1_visitors * self.avg_affiliate_ctr)
        phase1_conversions = int(phase1_hops * self.avg_affiliate_conversion)
        phase1_estimated_royalty = int(phase1_conversions * self.avg_bounty_royalty)

        # Financial modeling at 1M visitors
        phase2_hops = int(self.target_phase2_visitors * self.avg_affiliate_ctr)
        phase2_conversions = int(phase2_hops * self.avg_affiliate_conversion)
        phase2_estimated_royalty = int(phase2_conversions * self.avg_bounty_royalty)

        # Next High-Priority Strategic Targets (Niche Gap Matrix)
        strategic_clusters = [
            {
                "pillar": "AI Coding & Developer Productivity (Highest Tech Search Intent)",
                "priority": "IMMEDIATE",
                "target_tools": ["cursor", "v0-dev", "github-copilot", "replit", "lovable-dev"],
                "search_volume_tier": "VERY HIGH",
                "bounty_estimate": "$30 - $100 / paid dev"
            },
            {
                "pillar": "Go-to-Market & Sales Intelligence (Highest Enterprise LTV)",
                "priority": "HIGH",
                "target_tools": ["apollo-io", "clay-com", "lemlist", "instantly-ai", "hubspot"],
                "search_volume_tier": "HIGH",
                "bounty_estimate": "$100 - $350 / enterprise account"
            },
            {
                "pillar": "AI Voice & Generative Media (Viral Consumer & SMB Demand)",
                "priority": "HIGH",
                "target_tools": ["elevenlabs", "heygen", "descript", "synthesia", "runway"],
                "search_volume_tier": "VIRAL",
                "bounty_estimate": "$25 - $75 / creator"
            },
            {
                "pillar": "Enterprise Automation & Workflow OS (Recurring SaaS Moats)",
                "priority": "CORE",
                "target_tools": ["make", "zapier", "n8n", "clickup", "monday-com", "airtable"],
                "search_volume_tier": "HIGH",
                "bounty_estimate": "$50 - $200 / team seat"
            },
            {
                "pillar": "High-Converting Web & E-Commerce Infrastructure",
                "priority": "EXPANSION",
                "target_tools": ["webflow", "framer", "shopify", "printify", "beehiiv"],
                "search_volume_tier": "HIGH",
                "bounty_estimate": "$40 - $150 / active store"
            }
        ]

        # Strategic Recommendations
        recommendations = [
            "Maintain an average article dwell time > 4m 00s to trigger Google's top-tier 'Helpful Content' algorithmic boost.",
            "Deploy 3 in-depth comparative vs articles (e.g. Cursor AI vs GitHub Copilot 2026, Make vs n8n Enterprise).",
            "Broaden outbound affiliate redirection via edge /go/ endpoints to ensure 0ms latency for mobile readers.",
            "Syndicate viral 4-tweet authority teardowns to Twitter/X for each published guide using SocialGrowthAgent."
        ]

        strategy_payload = {
            "timestamp": datetime.now().isoformat(),
            "current_status": {
                "published_reviews": assets["reviews_count"],
                "published_articles": assets["articles_count"],
                "total_assets": total_assets
            },
            "milestone_progress": {
                "phase1_100k": {
                    "target_visitors": self.target_phase1_visitors,
                    "assets_required": assets_needed_for_100k,
                    "progress_percent": phase1_progress,
                    "estimated_monthly_hops": phase1_hops,
                    "estimated_monthly_royalty": f"${phase1_estimated_royalty:,}"
                },
                "phase2_1m": {
                    "target_visitors": self.target_phase2_visitors,
                    "assets_required": assets_needed_for_1m,
                    "progress_percent": phase2_progress,
                    "estimated_monthly_hops": phase2_hops,
                    "estimated_monthly_royalty": f"${phase2_estimated_royalty:,}"
                }
            },
            "strategic_clusters": strategic_clusters,
            "strategic_recommendations": recommendations
        }

        # Save for /sentinel/ and dashboard consumption
        strategy_json_path = self.data_dir / "growth-strategy.json"
        strategy_json_path.write_text(json.dumps(strategy_payload, indent=2), encoding="utf-8")

        # Generate Executive Markdown Strategy Report
        self.generate_markdown_report(strategy_payload)

        return strategy_payload

    def generate_markdown_report(self, payload: Dict[str, Any]):
        """Generates a comprehensive executive report in reports/."""
        report_path = self.reports_dir / "growth_vision_roadmap.md"
        p1 = payload["milestone_progress"]["phase1_100k"]
        p2 = payload["milestone_progress"]["phase2_1m"]

        md = f"""# 🔭 HeliaTech Executive Growth & Visitor Trajectory Blueprint
**Supervised by**: Chief Agent Helia & Helia-VisionaryStrategist
**Generated At**: {payload['timestamp'][:19].replace('T', ' ')} UTC
**Target Trajectory**: Phase 1: 100,000 Unique Visitors/mo ➔ Phase 2: 1,000,000 Unique Visitors/mo

---

## 1. Executive Summary & Fleet Velocity
- **Published Reviews**: {payload['current_status']['published_reviews']} audited software systems
- **Published Editorial Masterclasses**: {payload['current_status']['published_articles']} long-form guides
- **Total Operational Content Nodes**: {payload['current_status']['total_assets']} landing assets
- **Phase 1 Completion Velocity**: **{p1['progress_percent']}%** of required ranking assets landed
- **Phase 2 Completion Velocity**: **{p2['progress_percent']}%** of programmatic asset volume

---

## 2. Milestone Revenue & Traffic Projections

| Metric | Phase 1 (100k Milestone) | Phase 2 (1M Milestone) |
|---|---|---|
| **Monthly Unique Visitors** | **100,000** | **1,000,000** |
| **Outbound Affiliate Hops (CTR 12%)** | {p1['estimated_monthly_hops']:,} / mo | {p2['estimated_monthly_hops']:,} / mo |
| **Projected Conversions (3.5%)** | ~{int(p1['estimated_monthly_hops']*0.035):,} sales | ~{int(p2['estimated_monthly_hops']*0.035):,} sales |
| **Estimated Monthly Royalty Pipeline** | **{p1['estimated_monthly_royalty']}** | **{p2['estimated_monthly_royalty']}** |

---

## 3. High-Yield Strategic Clusters for Immediate Expansion
"""
        for cluster in payload["strategic_clusters"]:
            md += f"""
### ⚡ {cluster['pillar']}
- **Strategic Urgency**: `{cluster['priority']}`
- **Search Intent Tier**: `{cluster['search_volume_tier']}`
- **Estimated Affiliate Royalty Bounty**: `{cluster['bounty_estimate']}`
- **Recommended Software Targets**: `{'`, `'.join(cluster['target_tools'])}`
"""

        md += """
---

## 4. Architectural Directives for Chief Agent Helia
1. **Dwell Time Superiority**: Maintain strict article depth (> 2,500 words with drop-caps, interactive ROI calculators, and concrete code/workflow examples) to sustain an average dwell time above 4 minutes.
2. **Instant Edge Redirection**: All affiliate calls must resolve via Cloudflare Edge 302 rules (`site/public/_redirects`) to guarantee 0ms hop latency.
3. **Automated Social Syndication**: Trigger `SocialGrowthAgent` on every newly compiled guide to claim mindshare on Twitter/X and developer communities.
"""
        report_path.write_text(md, encoding="utf-8")
        print(f"✓ Executive Growth Blueprint generated at: {report_path}")


if __name__ == "__main__":
    agent = VisionaryGrowthAgent()
    blueprint = agent.generate_growth_blueprint()
    print(f"\n[VISIONARY STRATEGIST] Phase 1 Progress: {blueprint['milestone_progress']['phase1_100k']['progress_percent']}%")
    print(f"[VISIONARY STRATEGIST] Projected Phase 1 Monthly Royalty: {blueprint['milestone_progress']['phase1_100k']['estimated_monthly_royalty']}")
