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

export const collections = {
  reviews: reviewsCollection,
  blog: blogCollection,
};
