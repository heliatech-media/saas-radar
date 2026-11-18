import { defineCollection, z } from 'astro:content';

const reviewsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    name: z.string(),
    slug: z.string().optional(),
    tagline: z.string(),
    category: z.string(),
    rating: z.number(),
    website_url: z.string().url(),
    affiliate_url: z.string().url().optional(),
    summary: z.string(),
    best_for: z.string(),
    pros: z.array(z.string()),
    cons: z.array(z.string()),
    key_features: z.array(z.string()),
    pricing_tiers: z.array(z.object({
      name: z.string(),
      price: z.string(),
      billing_period: z.string().default('monthly'),
      features: z.array(z.string()),
      is_popular: z.boolean().optional().default(false),
    })),
    alternatives: z.array(z.string()),
    faqs: z.array(z.object({
      question: z.string(),
      answer: z.string(),
    })),
    roi_metrics: z.object({
      hours_saved_monthly: z.number(),
      financial_lift_monthly: z.string(),
      payback_period_weeks: z.number(),
      roi_summary: z.string(),
    }).optional(),
    benchmark_scores: z.object({
      performance: z.number(),
      ease_of_use: z.number(),
      value_for_money: z.number(),
      integrations: z.number(),
    }).optional(),
    competitor_matches: z.array(z.object({
      competitor: z.string(),
      key_advantage: z.string(),
      when_to_switch: z.string(),
    })).optional(),
  }),
});

const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    full_headline: z.string().optional(),
    seo_title: z.string().optional(),
    description: z.string(),
    date: z.string(),
    author: z.string().default('HELIA TECH'),
    category: z.string().default('Enquête SaaS'),
    tags: z.array(z.string()).default([]),
    image: z.string().optional(),
    readingTime: z.string().default('10 MIN'),
    tool_slug: z.string().optional(),
    tldr: z.array(z.string()).optional(),
    affiliate_cta: z.object({
      badge: z.string().optional(),
      title: z.string(),
      description: z.string(),
      button_text: z.string(),
      url: z.string(),
    }).optional(),
  }),
});

const reposCollection = defineCollection({
  type: 'content',
  schema: z.object({
    name: z.string(),
    repo_name: z.string(),
    repo_url: z.string().url(),
    category: z.string(),
    tagline: z.string(),
    stars: z.number(),
    forks: z.number(),
    open_issues: z.number(),
    last_commit: z.string(),
    license: z.string(),
    license_risk: z.enum(['Low', 'Medium', 'High']),
    health_score: z.number(),
    stack: z.array(z.string()),
    has_docker: z.boolean().default(false),
    has_tests: z.boolean().default(false),
    cloud_alternative_url: z.string().optional(),
    cloud_alternative_name: z.string().optional(),
    key_metrics: z.object({
      commit_frequency: z.string(),
      issue_response_time: z.string(),
      cve_status: z.string().default('Clean'),
      production_ready_rating: z.number(),
    }).optional(),
  }),
});

export const collections = {
  reviews: reviewsCollection,
  blog: blogCollection,
  repos: reposCollection,
};
