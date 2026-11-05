/**
 * HELIATECH DIGITAL TEMPLATES MARKETPLACE
 * Core TypeScript Definitions for the 29 Production Tables
 */

export type UserRole = 'USER' | 'SELLER' | 'ADMIN' | 'SUPER_ADMIN';

export type ProductPlatform = 'n8n' | 'make' | 'notion' | 'supabase' | 'airtable' | 'cursor' | 'zapier';
export type ProductStatus = 'draft' | 'pending_review' | 'published' | 'rejected' | 'suspended' | 'archived';
export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export interface SellerProfile {
  id: string;
  user_id: string;
  store_name: string;
  store_slug: string;
  bio?: string;
  logo_url?: string;
  banner_url?: string;
  website_url?: string;
  github_handle?: string;
  linkedin_url?: string;
  twitter_handle?: string;
  payout_method: 'stripe_connect' | 'paypal' | 'sepa';
  payout_account_id?: string;
  payout_email?: string;
  commission_rate: number; // e.g. 80.00%
  is_verified: boolean;
  verified_badge: string;
  status: 'active' | 'suspended' | 'pending_kyc' | 'archived';
  total_sales_count: number;
  total_gross_cents: number;
  total_net_earnings_cents: number;
  average_rating: number;
  created_at: string;
  updated_at: string;
}

export interface SellerApplication {
  id: string;
  user_id: string;
  applicant_name: string;
  applicant_email: string;
  portfolio_url?: string;
  expertise_areas: string[];
  sample_work_urls: string[];
  motivation_text: string;
  status: 'pending' | 'approved' | 'rejected' | 'under_review';
  admin_notes?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface MarketplaceCategory {
  id: string;
  parent_id?: string;
  name: string;
  slug: string;
  description?: string;
  icon: string;
  image_url?: string;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MarketplaceProduct {
  id: string;
  seller_id: string;
  category_id: string;
  title: string;
  slug: string;
  short_description: string;
  full_description: string;
  platform: ProductPlatform;
  difficulty_level: DifficultyLevel;
  price_cents: number; // integer cents (e.g. 4900 = $49.00 USD)
  discount_price_cents?: number;
  discount_expires_at?: string;
  currency: string;
  is_free: boolean;
  current_version: string;
  demo_video_url?: string;
  requirements: string[];
  whats_included: string[];
  installation_guide: string;
  documentation_url?: string;
  status: ProductStatus;
  rejection_reason?: string;
  is_featured: boolean;
  views_count: number;
  sales_count: number;
  revenue_gross_cents: number;
  average_rating: number;
  reviews_count: number;
  deleted_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ProductFile {
  id: string;
  product_id: string;
  file_name: string;
  file_vault_key: string;
  file_size_bytes: number;
  file_mime_type: string;
  file_sha256_hash: string;
  is_main_file: boolean;
  anti_scam_verified: boolean;
  anti_scam_score: number;
  created_at: string;
}

export interface ProductVersion {
  id: string;
  product_id: string;
  version_number: string;
  changelog: string;
  file_vault_key: string;
  release_date: string;
  is_current: boolean;
  created_at: string;
}

export interface ProductLicense {
  id: string;
  license_key: 'personal' | 'commercial' | 'extended' | 'agency';
  title: string;
  description: string;
  allowed_domains_count: number;
  resale_allowed: boolean;
  client_use_allowed: boolean;
  created_at: string;
}

export interface Order {
  id: string;
  order_number: string;
  buyer_user_id: string;
  buyer_email: string;
  buyer_company_name?: string;
  buyer_vat_number?: string;
  subtotal_cents: number;
  discount_cents: number;
  tax_cents: number;
  total_cents: number;
  currency: string;
  payment_status: 'pending' | 'paid' | 'failed' | 'refunded' | 'partially_refunded';
  invoice_number?: string;
  invoice_url?: string;
  created_at: string;
  updated_at: string;
}

export interface OrderItem {
  id: string;
  order_id: string;
  product_id: string;
  seller_id: string;
  license_id?: string;
  unit_price_cents: number;
  platform_commission_cents: number; // 20%
  seller_net_cents: number; // 80%
  created_at: string;
}

export interface Purchase {
  id: string;
  user_id: string;
  product_id: string;
  order_id: string;
  order_item_id: string;
  license_key: string;
  assigned_version: string;
  download_count: number;
  last_downloaded_at?: string;
  is_active: boolean;
  created_at: string;
}

export interface Review {
  id: string;
  product_id: string;
  user_id: string;
  order_id: string;
  rating: number; // 1 to 5
  title?: string;
  comment: string;
  status: 'published' | 'hidden' | 'flagged';
  created_at: string;
  updated_at: string;
}

export interface SellerPayout {
  id: string;
  seller_id: string;
  amount_cents: number;
  currency: string;
  provider: 'stripe_connect' | 'sepa';
  provider_payout_id?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  scheduled_for: string;
  paid_at?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface SupportTicket {
  id: string;
  user_id: string;
  seller_id: string;
  product_id?: string;
  order_id?: string;
  subject: string;
  category: 'integration' | 'bug' | 'question' | 'billing';
  status: 'open' | 'in_progress' | 'waiting_user' | 'resolved' | 'closed';
  priority: 'low' | 'normal' | 'urgent';
  created_at: string;
  updated_at: string;
}

export interface SupportMessage {
  id: string;
  ticket_id: string;
  sender_id: string;
  sender_role: 'buyer' | 'seller' | 'admin';
  message_text: string;
  attachment_urls: string[];
  is_read: boolean;
  created_at: string;
}

export interface AdminAuditLog {
  id: string;
  admin_user_id: string;
  action_type: string;
  target_entity: string;
  target_id: string;
  metadata: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}
