/**
 * HELIATECH DIGITAL TEMPLATES MARKETPLACE
 * Database Access Layer & Provider Interface
 * Supports Supabase / PostgreSQL REST API with resilient fallback
 */

import type { 
  MarketplaceProduct, 
  SellerProfile, 
  MarketplaceCategory, 
  Order, 
  Purchase, 
  Review, 
  SellerApplication 
} from './types';

export interface DatabaseConfig {
  supabaseUrl?: string;
  supabaseKey?: string;
}

export class MarketplaceDatabase {
  private url: string;
  private key: string;

  constructor(config?: DatabaseConfig) {
    this.url = config?.supabaseUrl || (typeof process !== 'undefined' ? process.env.SUPABASE_URL || '' : '');
    this.key = config?.supabaseKey || (typeof process !== 'undefined' ? process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || '' : '');
  }

  private get headers(): HeadersInit {
    return {
      'Content-Type': 'application/json',
      'apikey': this.key,
      'Authorization': `Bearer ${this.key}`
    };
  }

  private isConfigured(): boolean {
    return Boolean(this.url && this.key);
  }

  /**
   * Generic PostgREST fetcher
   */
  async query<T = any>(endpoint: string, options: RequestInit = {}): Promise<T[]> {
    if (!this.isConfigured()) {
      return [];
    }

    const res = await fetch(`${this.url}/rest/v1/${endpoint}`, {
      ...options,
      headers: {
        ...this.headers,
        ...(options.headers || {})
      }
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`Database Query Error [${res.status}]: ${errText}`);
    }

    return res.json();
  }

  // --- Products ---
  async getPublishedProducts(categorySlug?: string, limit = 50): Promise<MarketplaceProduct[]> {
    if (!this.isConfigured()) return [];
    let endpoint = `marketplace_products?status=eq.published&deleted_at=is.null&order=sales_count.desc&limit=${limit}`;
    if (categorySlug) {
      endpoint += `&category_slug=eq.${encodeURIComponent(categorySlug)}`;
    }
    return this.query<MarketplaceProduct>(endpoint);
  }

  async getProductBySlug(slug: string): Promise<MarketplaceProduct | null> {
    if (!this.isConfigured()) return null;
    const res = await this.query<MarketplaceProduct>(`marketplace_products?slug=eq.${encodeURIComponent(slug)}&limit=1`);
    return res[0] || null;
  }

  // --- Seller Profiles ---
  async getSellerBySlug(storeSlug: string): Promise<SellerProfile | null> {
    if (!this.isConfigured()) return null;
    const res = await this.query<SellerProfile>(`seller_profiles?store_slug=eq.${encodeURIComponent(storeSlug)}&limit=1`);
    return res[0] || null;
  }

  async getSellerByUserId(userId: string): Promise<SellerProfile | null> {
    if (!this.isConfigured()) return null;
    const res = await this.query<SellerProfile>(`seller_profiles?user_id=eq.${encodeURIComponent(userId)}&limit=1`);
    return res[0] || null;
  }

  // --- Purchases / Entitlements (Library) ---
  async getUserPurchases(userId: string): Promise<Purchase[]> {
    if (!this.isConfigured()) return [];
    return this.query<Purchase>(`purchases?user_id=eq.${encodeURIComponent(userId)}&is_active=eq.true&order=created_at.desc`);
  }

  // --- Categories ---
  async getActiveCategories(): Promise<MarketplaceCategory[]> {
    if (!this.isConfigured()) return [];
    return this.query<MarketplaceCategory>('marketplace_categories?is_active=eq.true&order=display_order.asc');
  }

  // --- Seller Applications ---
  async createSellerApplication(app: Omit<SellerApplication, 'id' | 'created_at' | 'updated_at'>): Promise<SellerApplication> {
    if (!this.isConfigured()) {
      // Fallback for local runtime
      return {
        ...app,
        id: `app_${Date.now()}`,
        status: 'pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
    }

    const res = await fetch(`${this.url}/rest/v1/seller_applications`, {
      method: 'POST',
      headers: {
        ...this.headers,
        'Prefer': 'return=representation'
      },
      body: JSON.stringify(app)
    });

    if (!res.ok) {
      throw new Error(`Failed to create application: ${await res.text()}`);
    }

    const json = await res.json();
    return json[0];
  }
}

export const db = new MarketplaceDatabase();
