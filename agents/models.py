"""
Pydantic Schemas for SaaS Directory & Multi-Agent Engine.
Defines strict data contracts for all agents.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PricingTier(BaseModel):
    name: str = Field(description="Plan name, e.g. Free, Starter, Pro, Enterprise")
    price: str = Field(description="Price string, e.g. '$0/mo', '$29/mo', 'Custom'")
    billing_period: str = Field(default="monthly", description="'monthly', 'yearly', or 'one-time'")
    features: List[str] = Field(description="Key features included in this tier")
    is_popular: bool = Field(default=False, description="Whether this is the highlighted tier")


class FAQItem(BaseModel):
    question: str = Field(description="Frequently asked question")
    answer: str = Field(description="Clear, authoritative answer")


class ROIMetrics(BaseModel):
    hours_saved_monthly: int = Field(default=18, description="Estimated hours saved per month for an average team using this tool")
    financial_lift_monthly: str = Field(default="$950/mo", description="Estimated financial productivity value unlocked per month, e.g. '$950/mo'")
    payback_period_weeks: float = Field(default=2.0, description="Weeks required for productivity savings to recoup license cost")
    roi_summary: str = Field(default="", description="1-2 sentence concrete rationale explaining where cost savings and revenue lift come from")


class BenchmarkScores(BaseModel):
    performance: float = Field(default=9.2, ge=1.0, le=10.0, description="Technical execution speed and uptime score out of 10")
    ease_of_use: float = Field(default=8.6, ge=1.0, le=10.0, description="Onboarding, learning curve and UX score out of 10")
    value_for_money: float = Field(default=9.0, ge=1.0, le=10.0, description="Pricing competitiveness vs feature allowance out of 10")
    integrations: float = Field(default=8.8, ge=1.0, le=10.0, description="API robustness and third-party app ecosystem out of 10")


class CompetitorMatch(BaseModel):
    competitor: str = Field(description="Name of direct competitor, e.g. 'Zapier'")
    key_advantage: str = Field(description="Why pick this tool over competitor in 1 punchy sentence")
    when_to_switch: str = Field(description="Exact condition when the user should choose the competitor instead")


class ToolReview(BaseModel):
    name: str = Field(description="Official name of the SaaS product")
    slug: str = Field(description="URL-friendly kebab-case slug, e.g. 'notion-ai'")
    tagline: str = Field(description="Catchy 1-sentence value proposition")
    category: str = Field(description="Primary category, e.g. 'AI Writing', 'CRM', 'Video Automation', 'Productivity'")
    rating: float = Field(ge=1.0, le=5.0, description="Overall score out of 5.0 (e.g. 4.8)")
    website_url: str = Field(description="Official website URL")
    affiliate_url: Optional[str] = Field(default="", description="Affiliate link or redirect URL")
    summary: str = Field(description="2-3 sentence executive summary of what the tool does")
    best_for: str = Field(description="Specific target audience, e.g. 'Freelancers, remote teams, and solo creators'")
    pros: List[str] = Field(description="Top 4-5 genuine pros/strengths")
    cons: List[str] = Field(description="Top 2-3 realistic drawbacks or limitations")
    key_features: List[str] = Field(description="Top 5 core standout features")
    pricing_tiers: List[PricingTier] = Field(description="List of pricing plans")
    alternatives: List[str] = Field(description="Names of top 3 direct competitors")
    detailed_verdict: str = Field(description="In-depth 3-4 paragraph technical review and final recommendation")
    faqs: List[FAQItem] = Field(description="3-4 high-intent FAQs (great for Google rich snippets)")
    roi_metrics: Optional[ROIMetrics] = Field(default_factory=ROIMetrics, description="Concrete financial and time savings analysis")
    benchmark_scores: Optional[BenchmarkScores] = Field(default_factory=BenchmarkScores, description="Granular scores across 4 key dimensions")
    competitor_matches: Optional[List[CompetitorMatch]] = Field(default_factory=list, description="Head-to-head comparison cards vs main rivals")


class ComparisonArticle(BaseModel):
    title: str = Field(description="SEO title, e.g. 'Make vs Zapier 2026: Which Automation Tool is Best?'")
    slug: str = Field(description="URL slug, e.g. 'make-vs-zapier'")
    tool_a: str = Field(description="Name of first tool")
    tool_b: str = Field(description="Name of second tool")
    winner: str = Field(description="Overall winner and why")
    summary: str = Field(description="Executive breakdown of the comparison")
    comparison_table: List[dict] = Field(description="Criteria, Tool A score/notes, Tool B score/notes")
    faqs: List[FAQItem]


class RadarKeyword(BaseModel):
    tool_name: str
    category: str
    search_intent: str
    primary_affiliate_network: str
    average_commission: str
