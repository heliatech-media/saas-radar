"""
Agent 3: Content Publisher & Markdown Architect.
Transforms Pydantic data models into pristine Astro Markdown files with rich frontmatter
and maintains the search index.
"""

import json
from pathlib import Path
from typing import List
import yaml
from agents.config import CONTENT_DIR, BLOG_CONTENT_DIR, DATA_DIR
from agents.models import ToolReview, BlogPost


class PublisherAgent:
    def __init__(self, content_dir: Path = CONTENT_DIR, blog_dir: Path = BLOG_CONTENT_DIR, data_dir: Path = DATA_DIR):
        self.content_dir = content_dir
        self.blog_dir = blog_dir
        self.data_dir = data_dir
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.blog_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def publish_review(self, review: ToolReview) -> Path:
        """Writes an Astro-compatible Markdown review with structured YAML frontmatter."""
        filename = f"{review.slug}.md"
        filepath = self.content_dir / filename

        frontmatter = {
            "name": review.name,
            "slug": review.slug,
            "tagline": review.tagline,
            "category": review.category,
            "rating": review.rating,
            "website_url": review.website_url,
            "affiliate_url": review.affiliate_url or review.website_url,
            "summary": review.summary,
            "best_for": review.best_for,
            "pros": review.pros,
            "cons": review.cons,
            "key_features": review.key_features,
            "pricing_tiers": [tier.model_dump() for tier in review.pricing_tiers],
            "alternatives": review.alternatives,
            "faqs": [faq.model_dump() for faq in review.faqs],
        }

        if review.roi_metrics:
            frontmatter["roi_metrics"] = review.roi_metrics.model_dump()
        if review.benchmark_scores:
            frontmatter["benchmark_scores"] = review.benchmark_scores.model_dump()
        if review.competitor_matches:
            frontmatter["competitor_matches"] = [c.model_dump() for c in review.competitor_matches]

        # Format clean markdown with YAML frontmatter and detailed body
        yaml_header = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        content = f"""---
{yaml_header}---

## Executive Summary

{review.summary}

### Who is {review.name} Best For?
**Target Audience:** {review.best_for}

## Key Features & Capabilities

{"".join([f"- **{feature}**\n" for feature in review.key_features])}

## Pricing Overview

| Plan | Price | Billing | Key Highlights |
| :--- | :--- | :--- | :--- |
{"".join([f"| **{tier.name}** | {tier.price} | {tier.billing_period} | {', '.join(tier.features[:2])} |\n" for tier in review.pricing_tiers])}

## Pros & Cons

### Pros
{"".join([f"- {pro}\n" for pro in review.pros])}

### Cons
{"".join([f"- {con}\n" for con in review.cons])}

## Detailed Verdict & Technical Analysis

{review.detailed_verdict}

## Frequently Asked Questions

{"".join([f"### {faq.question}\n\n{faq.answer}\n\n" for faq in review.faqs])}
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # Update the search and directory index
        self._update_index(review)

        return filepath

    def publish_blog_post(self, post: BlogPost) -> Path:
        """Writes an Astro-compatible Markdown blog post with structured YAML frontmatter."""
        filename = f"{post.slug}.md"
        filepath = self.blog_dir / filename

        frontmatter = {
            "title": post.title,
            "description": post.description,
            "date": post.date,
            "author": post.author,
            "category": post.category,
            "tags": post.tags,
            "readingTime": post.readingTime,
            "tool_slug": post.tool_slug,
            "tldr": post.tldr,
            "affiliate_cta": post.affiliate_cta.model_dump(),
        }

        yaml_header = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        full_content = f"""---
{yaml_header}---

{post.markdown_content}
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        return filepath

    def _update_index(self, review: ToolReview):
        """Updates the local JSON index used by the homepage for instant search & filtering."""
        index_file = self.data_dir / "tools-index.json"
        tools = []
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    tools = json.load(f)
            except Exception:
                tools = []

        # Remove existing entry if updating
        tools = [t for t in tools if t.get("slug") != review.slug]

        starting_price = "Free"
        for tier in review.pricing_tiers:
            if "free" not in tier.name.lower() and "$" in tier.price:
                starting_price = tier.price
                break

        tools.append({
            "name": review.name,
            "slug": review.slug,
            "tagline": review.tagline,
            "category": review.category,
            "rating": review.rating,
            "starting_price": starting_price,
            "best_for": review.best_for,
            "affiliate_url": review.affiliate_url or review.website_url,
        })

        # Sort alphabetically by name
        tools.sort(key=lambda x: x["name"])

        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(tools, f, indent=2, ensure_ascii=False)
