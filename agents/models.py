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
