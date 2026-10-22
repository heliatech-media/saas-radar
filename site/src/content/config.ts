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
  }),
});

export const collections = {
  reviews: reviewsCollection,
};
