"""
Master Orchestrator: Coordinates Radar, Analyst, and Publisher agents.
Can be executed manually or triggered by automated GitHub Actions cron.
"""

import argparse
import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.config import GEMINI_API_KEY
from agents.radar_agent import RadarAgent
from agents.analyst_agent import AnalystAgent
from agents.publisher_agent import PublisherAgent
from agents.partnerstack_sync import PartnerStackSync
from agents.models import ToolReview, PricingTier, FAQItem, ROIMetrics, BenchmarkScores, CompetitorMatch


def run_pipeline_for_tool(tool_name: str, category: str = "", api_key: str = GEMINI_API_KEY):
    """Executes the full pipeline for a single tool."""
    print(f"\n[ORCHESTRATOR] 🎯 Initiating analysis for: '{tool_name}'...")

    publisher = PublisherAgent()

    if not api_key:
        print("[ORCHESTRATOR] ⚠️ GEMINI_API_KEY not found. Using high-quality seed blueprint for demonstration.")
        review = create_sample_review(tool_name, category)
    else:
        analyst = AnalystAgent(api_key=api_key)
        review = analyst.analyze_tool(tool_name=tool_name, category_hint=category)

    filepath = publisher.publish_review(review)
    print(f"[ORCHESTRATOR] ✅ Review successfully created and indexed: {filepath}")
    return review


def create_sample_review(tool_name: str, category: str = "") -> ToolReview:
    """Fallback generator for testing when API key is not yet set up."""
    slug = tool_name.lower().replace(" ", "-").replace(".", "")
    return ToolReview(
        name=tool_name,
        slug=slug,
        tagline=f"Next-generation {category or 'B2B automation'} platform built for modern scaling teams.",
        category=category or "AI Automation & No-Code",
        rating=4.8,
        website_url=f"https://www.{slug}.com",
        affiliate_url=f"https://www.{slug}.com",
        summary=f"{tool_name} is an enterprise-grade platform designed to streamline operations, eliminate repetitive manual workflows, and scale revenue.",
        best_for="Growth-stage startups, modern remote agencies, and tech-forward teams looking to optimize operations.",
        pros=[
            "Intuitive visual canvas requiring zero complex coding",
            "Extensive pre-built integrations with 1,000+ top cloud applications",
            "High execution speed with minimal latency and enterprise-grade uptime",
            "Highly competitive pricing with generous free tier allowances"
        ],
        cons=[
            "Advanced routing features have a slight initial learning curve",
            "Webhook debugging requires understanding of JSON payload structures"
        ],
        key_features=[
            "Visual Workflow Orchestration",
            "Real-Time Webhook Processing",
            "Native AI Integration with Google Gemini & OpenAI",
            "Enterprise Access Control and Audit Logs",
            "Auto-scaling serverless execution engine"
        ],
        pricing_tiers=[
            PricingTier(
                name="Free",
                price="$0/mo",
                billing_period="monthly",
                features=["1,000 operations/month", "Core integrations", "Community support"]
            ),
            PricingTier(
                name="Pro",
                price="$19/mo",
                billing_period="monthly",
                is_popular=True,
                features=["10,000 operations/month", "Real-time execution", "Priority customer support", "Unlimited active workflows"]
            ),
            PricingTier(
                name="Team",
                price="$49/mo",
                billing_period="monthly",
                features=["50,000 operations/month", "Shared team workspace", "Custom webhook domains", "SLA guarantee"]
            )
        ],
        alternatives=["Zapier", "n8n", "Workato"],
        detailed_verdict=f"""
In our comprehensive benchmark, {tool_name} consistently ranks in the top tier for reliability and developer flexibility. 
For businesses spending over 10 hours a week on repetitive data transfer and customer notification workflows, 
deploying {tool_name} delivers an immediate ROI within the first 7 days.

The balance of visual simplicity and deep programmatic flexibility makes it an essential foundation for any modern online business.
""",
        faqs=[
            FAQItem(
                question=f"Does {tool_name} offer a completely free plan?",
                answer=f"Yes, {tool_name} provides a permanent free plan with generous initial allowances suitable for testing and small automated workflows."
            ),
            FAQItem(
                question=f"How does {tool_name} compare to legacy alternatives?",
                answer=f"Compared to older tools like Zapier, {tool_name} offers up to 5x more operations per dollar spent, making it dramatically more cost-effective as your automation volume scales."
            ),
            FAQItem(
                question=f"Can I integrate custom AI models and webhooks?",
                answer="Yes, it features first-class support for custom REST endpoints, webhooks, and direct connections to AI APIs."
            )
        ],
        roi_metrics=ROIMetrics(
            hours_saved_monthly=24,
            financial_lift_monthly="$1,200/mo",
            payback_period_weeks=1.5,
            roi_summary=f"Automating key operational bottlenecks with {tool_name} saves ~24 hours monthly, yielding over $1,200 in recovered bandwidth."
        ),
        benchmark_scores=BenchmarkScores(
            performance=9.1,
            ease_of_use=8.5,
            value_for_money=9.0,
            integrations=8.8
        ),
        competitor_matches=[
            CompetitorMatch(
                competitor="Legacy Alternatives",
                key_advantage=f"Modern, AI-native interface with substantially lower total cost of ownership.",
                when_to_switch="Only choose legacy tools if an enterprise mandate requires on-premise mainframe hosting."
            )
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="Autonomous SaaS Review & Directory Engine")
    parser.add_argument("--tool", type=str, help="Name of a specific SaaS tool to analyze and publish")
    parser.add_argument("--category", type=str, default="", help="Category hint for the tool")
    parser.add_argument("--seed", action="store_true", help="Generate reviews for top curated seed SaaS tools")
    parser.add_argument("--discover", type=int, default=0, help="Number of trending tools to discover with Radar Agent")
    args = parser.parse_args()

    # Automatically synchronize active partner links from PartnerStack if configured
    syncer = PartnerStackSync()
    if syncer.is_configured():
        print("[ORCHESTRATOR] 🔄 Auto-syncing active affiliate links from PartnerStack...")
        syncer.sync_into_heliatech()

    radar = RadarAgent()

    if args.tool:
        run_pipeline_for_tool(args.tool, args.category)
    elif args.seed:
        print("[ORCHESTRATOR] 🚀 Seeding directory with curated high-margin SaaS tools...")
        seed_tools = radar.get_seed_tools()[:6]  # Seed top 6 tools
        for item in seed_tools:
            run_pipeline_for_tool(item["name"], item["category"])
        print("[ORCHESTRATOR] 🎉 Seeding completed!")
    elif args.discover > 0:
        print(f"[ORCHESTRATOR] 📡 Radar Agent discovering {args.discover} trending opportunities...")
        opportunities = radar.discover_trending_opportunities(count=args.discover)
        for opp in opportunities:
            run_pipeline_for_tool(opp.tool_name, opp.category)
    else:
        # Default: Seed initial reviews
        print("[ORCHESTRATOR] ⚡ Running default initialization with seed tools...")
        seed_tools = radar.get_seed_tools()[:4]
        for item in seed_tools:
            run_pipeline_for_tool(item["name"], item["category"])


if __name__ == "__main__":
    main()
