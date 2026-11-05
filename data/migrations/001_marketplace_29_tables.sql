-- ============================================================================
-- HELIATECH DIGITAL TEMPLATES MARKETPLACE — PRODUCTION DATABASE MIGRATION 001
-- Multi-Vendor Architecture: 29 Tables, Foreign Keys, Strict Indexes & RLS Policies
-- Compatible with PostgreSQL 15+ & Supabase Database
-- ============================================================================

-- Enable required cryptographic extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Utility function: automatic updated_at timestamp trigger
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 1. IDENTITÉ, VENDEURS & CANDIDATURES
-- ============================================================================

-- Table 1: Profils Vendeurs
CREATE TABLE IF NOT EXISTS public.seller_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE, -- Lié au compte utilisateur centralisé (auth.users)
    store_name VARCHAR(120) NOT NULL,
    store_slug VARCHAR(140) NOT NULL UNIQUE,
    bio TEXT,
    logo_url VARCHAR(500),
    banner_url VARCHAR(500),
    website_url VARCHAR(255),
    github_handle VARCHAR(100),
    linkedin_url VARCHAR(255),
    twitter_handle VARCHAR(100),
    payout_method VARCHAR(50) DEFAULT 'stripe_connect', -- 'stripe_connect' | 'paypal' | 'sepa'
    payout_account_id VARCHAR(255),
    payout_email VARCHAR(255),
    commission_rate NUMERIC(4, 2) DEFAULT 80.00, -- 80% créateur par défaut
    is_verified BOOLEAN DEFAULT FALSE,
    verified_badge VARCHAR(50) DEFAULT 'verified_creator',
    status VARCHAR(30) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'pending_kyc', 'archived')),
    total_sales_count INTEGER DEFAULT 0,
    total_gross_cents BIGINT DEFAULT 0,
    total_net_earnings_cents BIGINT DEFAULT 0,
    average_rating NUMERIC(3, 2) DEFAULT 5.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_seller_profiles_slug ON public.seller_profiles (store_slug);
CREATE INDEX IF NOT EXISTS idx_seller_profiles_user ON public.seller_profiles (user_id);
CREATE INDEX IF NOT EXISTS idx_seller_profiles_status ON public.seller_profiles (status);

-- Table 2: Candidatures Vendeurs (Applications)
CREATE TABLE IF NOT EXISTS public.seller_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    applicant_name VARCHAR(150) NOT NULL,
    applicant_email VARCHAR(255) NOT NULL,
    portfolio_url VARCHAR(500),
    expertise_areas TEXT[] DEFAULT '{}', -- ['n8n', 'Make', 'AI Agents', 'Airtable', 'Supabase']
    sample_work_urls TEXT[] DEFAULT '{}',
    motivation_text TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'under_review')),
    admin_notes TEXT,
    reviewed_by UUID,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_seller_apps_status ON public.seller_applications (status);
CREATE INDEX IF NOT EXISTS idx_seller_apps_user ON public.seller_applications (user_id);

-- ============================================================================
-- 2. TAXONOMIE & PRODUITS
-- ============================================================================

-- Table 3: Catégories & Sous-Catégories
CREATE TABLE IF NOT EXISTS public.marketplace_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES public.marketplace_categories(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50) DEFAULT '⚡',
    image_url VARCHAR(500),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_categories_slug ON public.marketplace_categories (slug);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON public.marketplace_categories (parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_order ON public.marketplace_categories (display_order);

-- Table 4: Produits & Templates
CREATE TABLE IF NOT EXISTS public.marketplace_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID NOT NULL REFERENCES public.seller_profiles(id) ON DELETE RESTRICT,
    category_id UUID NOT NULL REFERENCES public.marketplace_categories(id) ON DELETE RESTRICT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(240) NOT NULL UNIQUE,
    short_description VARCHAR(300) NOT NULL,
    full_description TEXT NOT NULL,
    platform VARCHAR(50) NOT NULL, -- 'n8n' | 'make' | 'notion' | 'supabase' | 'airtable' | 'cursor' | 'zapier'
    difficulty_level VARCHAR(30) DEFAULT 'intermediate' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced', 'expert')),
    price_cents INTEGER NOT NULL DEFAULT 0, -- Montant exact en centimes (ex: 4900 = 49.00 USD), 0 = Free
    discount_price_cents INTEGER,
    discount_expires_at TIMESTAMP WITH TIME ZONE,
    currency VARCHAR(3) DEFAULT 'USD',
    is_free BOOLEAN DEFAULT FALSE,
    current_version VARCHAR(30) DEFAULT '1.0.0',
    demo_video_url VARCHAR(500),
    requirements TEXT[] DEFAULT '{}',
    whats_included TEXT[] DEFAULT '{}',
    installation_guide TEXT NOT NULL,
    documentation_url VARCHAR(500),
    status VARCHAR(30) DEFAULT 'pending_review' CHECK (status IN ('draft', 'pending_review', 'published', 'rejected', 'suspended', 'archived')),
    rejection_reason TEXT,
    is_featured BOOLEAN DEFAULT FALSE,
    views_count INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    revenue_gross_cents BIGINT DEFAULT 0,
    average_rating NUMERIC(3, 2) DEFAULT 5.00,
    reviews_count INTEGER DEFAULT 0,
    deleted_at TIMESTAMP WITH TIME ZONE, -- Soft delete
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_products_slug ON public.marketplace_products (slug);
CREATE INDEX IF NOT EXISTS idx_products_seller ON public.marketplace_products (seller_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.marketplace_products (category_id);
CREATE INDEX IF NOT EXISTS idx_products_platform ON public.marketplace_products (platform);
CREATE INDEX IF NOT EXISTS idx_products_status ON public.marketplace_products (status);
CREATE INDEX IF NOT EXISTS idx_products_price ON public.marketplace_products (price_cents);
CREATE INDEX IF NOT EXISTS idx_products_featured ON public.marketplace_products (is_featured, status);

-- Table 5: Médias Produits (Galerie d'images)
CREATE TABLE IF NOT EXISTS public.product_media (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE CASCADE,
    media_type VARCHAR(20) DEFAULT 'image' CHECK (media_type IN ('image', 'video', 'diagram')),
    url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(200),
    is_thumbnail BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_product_media_product ON public.product_media (product_id);

-- Table 6: Fichiers Produits (Stockage Privé Sécurisé)
CREATE TABLE IF NOT EXISTS public.product_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_vault_key VARCHAR(500) NOT NULL, -- Clé d'objet dans le bucket privé (R2 / Storage)
    file_size_bytes BIGINT NOT NULL,
    file_mime_type VARCHAR(100) NOT NULL,
    file_sha256_hash VARCHAR(64) NOT NULL,
    is_main_file BOOLEAN DEFAULT TRUE,
    anti_scam_verified BOOLEAN DEFAULT FALSE,
    anti_scam_score INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_product_files_product ON public.product_files (product_id);

-- Table 7: Versions des Produits & Historique des Mises à Jour (Changelog)
CREATE TABLE IF NOT EXISTS public.product_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE CASCADE,
    version_number VARCHAR(30) NOT NULL,
    changelog TEXT NOT NULL,
    file_vault_key VARCHAR(500) NOT NULL,
    release_date TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_product_versions_product ON public.product_versions (product_id, version_number);

-- Table 8: Tags
CREATE TABLE IF NOT EXISTS public.product_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(60) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_product_tags_slug ON public.product_tags (slug);

-- Table 9: Relations Produits <-> Tags
CREATE TABLE IF NOT EXISTS public.product_tag_relations (
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES public.product_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_id)
);

-- Table 10: Types de Licences Configurables
CREATE TABLE IF NOT EXISTS public.product_licenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    license_key VARCHAR(50) NOT NULL UNIQUE, -- 'personal' | 'commercial' | 'extended' | 'agency'
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    allowed_domains_count INTEGER DEFAULT 1, -- -1 = illimité
    resale_allowed BOOLEAN DEFAULT FALSE,
    client_use_allowed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ============================================================================
-- 3. ENGAGEMENT, SOCIAL & MODÉRATION
-- ============================================================================

-- Table 11: Favoris Acheteurs (Wishlist)
CREATE TABLE IF NOT EXISTS public.product_favorites (
    user_id UUID NOT NULL,
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    PRIMARY KEY (user_id, product_id)
);
CREATE INDEX IF NOT EXISTS idx_favorites_user ON public.product_favorites (user_id);

-- Table 12: Avis Vérifiés Post-Achat (Reviews)
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    order_id UUID NOT NULL, -- Vérification de l'achat obligatoire
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(120),
    comment TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'published' CHECK (status IN ('published', 'hidden', 'flagged')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT uq_user_product_review UNIQUE (user_id, product_id)
);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON public.reviews (product_id);

-- Table 13: Réponses des Vendeurs aux Avis
CREATE TABLE IF NOT EXISTS public.review_replies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL UNIQUE REFERENCES public.reviews(id) ON DELETE CASCADE,
    seller_id UUID NOT NULL REFERENCES public.seller_profiles(id) ON DELETE CASCADE,
    reply_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Table 14: Signalements Produits (Reports)
CREATE TABLE IF NOT EXISTS public.product_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE CASCADE,
    reporter_user_id UUID NOT NULL,
    reason_category VARCHAR(50) NOT NULL, -- 'malware', 'phishing', 'copyright', 'misleading', 'secret_leak'
    details TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'dismissed')),
    admin_action TEXT,
    resolved_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reports_status ON public.product_reports (status);

-- ============================================================================
-- 4. VENTES, COMMANDES & TRANSACTIONS (Append-Only Ledger)
-- ============================================================================

-- Table 15: Commandes (Orders)
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) NOT NULL UNIQUE,
    buyer_user_id UUID NOT NULL,
    buyer_email VARCHAR(255) NOT NULL,
    buyer_company_name VARCHAR(150),
    buyer_vat_number VARCHAR(80),
    subtotal_cents INTEGER NOT NULL,
    discount_cents INTEGER DEFAULT 0,
    tax_cents INTEGER DEFAULT 0,
    total_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_status VARCHAR(30) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded', 'partially_refunded')),
    invoice_number VARCHAR(60) UNIQUE,
    invoice_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_buyer_id ON public.orders (buyer_user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders (payment_status);
CREATE INDEX IF NOT EXISTS idx_orders_number ON public.orders (order_number);

-- Table 16: Lignes de Commande (Order Items - Prix Historique Gelé)
CREATE TABLE IF NOT EXISTS public.order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE RESTRICT,
    seller_id UUID NOT NULL REFERENCES public.seller_profiles(id) ON DELETE RESTRICT,
    license_id UUID REFERENCES public.product_licenses(id),
    unit_price_cents INTEGER NOT NULL, -- Prix gelé au moment précis de l'achat
    platform_commission_cents INTEGER NOT NULL, -- 20% HeliaTech
    seller_net_cents INTEGER NOT NULL, -- 80% Vendeur
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON public.order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_seller ON public.order_items (seller_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON public.order_items (product_id);

-- Table 17: Bibliothèque Personnelle des Acheteurs (Purchases / Entitlements)
CREATE TABLE IF NOT EXISTS public.purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE RESTRICT,
    order_id UUID NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    order_item_id UUID NOT NULL REFERENCES public.order_items(id) ON DELETE CASCADE,
    license_key VARCHAR(100) NOT NULL UNIQUE,
    assigned_version VARCHAR(30) NOT NULL,
    download_count INTEGER DEFAULT 0,
    last_downloaded_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT uq_user_product_purchase UNIQUE (user_id, product_id)
);
CREATE INDEX IF NOT EXISTS idx_purchases_user ON public.purchases (user_id);
CREATE INDEX IF NOT EXISTS idx_purchases_product ON public.purchases (product_id);

-- Table 18: Paiements & Transactions
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES public.orders(id) ON DELETE RESTRICT,
    provider VARCHAR(50) NOT NULL, -- 'stripe' | 'lemon_squeezy' | 'paddle'
    provider_transaction_id VARCHAR(255) NOT NULL UNIQUE,
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(30) NOT NULL CHECK (status IN ('succeeded', 'pending', 'failed', 'reversed')),
    payment_method_type VARCHAR(50),
    receipt_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_payments_order ON public.payments (order_id);
CREATE INDEX IF NOT EXISTS idx_payments_provider_tx ON public.payments (provider_transaction_id);

-- Table 19: Journal des Événements Webhooks (Idempotence Stricte)
CREATE TABLE IF NOT EXISTS public.payment_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(50) NOT NULL,
    event_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    processed_status VARCHAR(20) DEFAULT 'processed' CHECK (processed_status IN ('processed', 'failed', 'ignored')),
    error_message TEXT,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT uq_provider_event UNIQUE (provider, event_id)
);
CREATE INDEX IF NOT EXISTS idx_payment_events_lookup ON public.payment_events (provider, event_id);

-- ============================================================================
-- 5. BUNDLES & PROMOTIONS
-- ============================================================================

-- Table 20: Offres Groupées (Product Bundles)
CREATE TABLE IF NOT EXISTS public.product_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID NOT NULL REFERENCES public.seller_profiles(id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    slug VARCHAR(170) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    banner_url VARCHAR(500),
    bundle_price_cents INTEGER NOT NULL,
    original_total_cents INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Table 21: Éléments Inclus dans les Bundles
CREATE TABLE IF NOT EXISTS public.bundle_items (
    bundle_id UUID NOT NULL REFERENCES public.product_bundles(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.marketplace_products(id) ON DELETE CASCADE,
    PRIMARY KEY (bundle_id, product_id)
);

-- Table 22: Promotions & Coupons Vendeurs
CREATE TABLE IF NOT EXISTS public.seller_promotions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID NOT NULL REFERENCES public.seller_profiles(id) ON DELETE CASCADE,
    coupon_code VARCHAR(40) NOT NULL UNIQUE,
    discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed_cents')),
    discount_value INTEGER NOT NULL, -- e.g. 20 (pour 20%) ou 1000 (pour $10.00)
    min_order_cents INTEGER DEFAULT 0,
    max_redemptions INTEGER,
    redemptions_count INTEGER DEFAULT 0,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Table 23: Utilisations de Coupons (Promotion Redemptions)
CREATE TABLE IF NOT EXISTS public.promotion_redemptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    promotion_id UUID NOT NULL REFERENCES public.seller_promotions(id) ON DELETE CASCADE,
    order_id UUID NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    discount_applied_cents INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- ============================================================================
-- 6. FINANCES & REVERSEMENTS VENDEURS (PAYOUTS)
-- ============================================================================

-- Table 24: Relevés de Reversements Vendeurs (Payouts 80%)
CREATE TABLE IF NOT EXISTS public.seller_payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID NOT NULL REFERENCES public.seller_profiles(id) ON DELETE RESTRICT,
    amount_cents BIGINT NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    provider VARCHAR(50) NOT NULL, -- 'stripe_connect' | 'sepa'
    provider_payout_id VARCHAR(255),
    status VARCHAR(30) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    scheduled_for TIMESTAMP WITH TIME ZONE NOT NULL,
    paid_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_seller_payouts_seller ON public.seller_payouts (seller_id);
CREATE INDEX IF NOT EXISTS idx_seller_payouts_status ON public.seller_payouts (status);

-- ============================================================================
-- 7. SUPPORT & SERVICE APRÈS-VENTE
-- ============================================================================

-- Table 25: Tickets de Support
CREATE TABLE IF NOT EXISTS public.support_tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    seller_id UUID NOT NULL REFERENCES public.seller_profiles(id) ON DELETE RESTRICT,
    product_id UUID REFERENCES public.marketplace_products(id) ON DELETE SET NULL,
    order_id UUID REFERENCES public.orders(id) ON DELETE SET NULL,
    subject VARCHAR(200) NOT NULL,
    category VARCHAR(50) DEFAULT 'integration', -- 'integration' | 'bug' | 'question' | 'billing'
    status VARCHAR(30) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'waiting_user', 'resolved', 'closed')),
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'urgent')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_support_tickets_user ON public.support_tickets (user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_seller ON public.support_tickets (seller_id);

-- Table 26: Messages de Support
CREATE TABLE IF NOT EXISTS public.support_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES public.support_tickets(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL,
    sender_role VARCHAR(20) NOT NULL CHECK (sender_role IN ('buyer', 'seller', 'admin')),
    message_text TEXT NOT NULL,
    attachment_urls TEXT[] DEFAULT '{}',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_support_messages_ticket ON public.support_messages (ticket_id);

-- ============================================================================
-- 8. NOTIFICATIONS & AUDIT TRAIL
-- ============================================================================

-- Table 27: Notifications Vendeurs
CREATE TABLE IF NOT EXISTS public.seller_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID NOT NULL REFERENCES public.seller_profiles(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL, -- 'sale_completed', 'product_approved', 'product_rejected', 'new_review', 'payout_sent'
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    link_url VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_seller_notifs ON public.seller_notifications (seller_id, is_read);

-- Table 28: Notifications Acheteurs (Marketplace Notifications)
CREATE TABLE IF NOT EXISTS public.marketplace_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- 'product_update', 'ticket_reply', 'receipt_ready'
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    link_url VARCHAR(500),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_user_notifs ON public.marketplace_notifications (user_id, is_read);

-- Table 29: Journal d'Audit Administrateur (Admin Audit Logs)
CREATE TABLE IF NOT EXISTS public.admin_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID NOT NULL,
    action_type VARCHAR(80) NOT NULL, -- 'approve_product', 'reject_product', 'approve_seller', 'suspend_seller', 'override_commission', 'resolve_report'
    target_entity VARCHAR(50) NOT NULL,
    target_id UUID NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_admin_audit_logs_action ON public.admin_audit_logs (action_type, target_entity);

-- ============================================================================
-- 9. TRIGGERS POUR UPDATED_AT AUTOMATIQUE
-- ============================================================================
CREATE OR REPLACE TRIGGER trg_seller_profiles_upd BEFORE UPDATE ON public.seller_profiles FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
CREATE OR REPLACE TRIGGER trg_seller_apps_upd BEFORE UPDATE ON public.seller_applications FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
CREATE OR REPLACE TRIGGER trg_categories_upd BEFORE UPDATE ON public.marketplace_categories FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
CREATE OR REPLACE TRIGGER trg_products_upd BEFORE UPDATE ON public.marketplace_products FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
CREATE OR REPLACE TRIGGER trg_orders_upd BEFORE UPDATE ON public.orders FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
CREATE OR REPLACE TRIGGER trg_bundles_upd BEFORE UPDATE ON public.product_bundles FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
CREATE OR REPLACE TRIGGER trg_payouts_upd BEFORE UPDATE ON public.seller_payouts FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
CREATE OR REPLACE TRIGGER trg_tickets_upd BEFORE UPDATE ON public.support_tickets FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- ============================================================================
-- 10. POLITIQUES ROW-LEVEL SECURITY (RLS)
-- ============================================================================
ALTER TABLE public.seller_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.marketplace_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.product_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.seller_payouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_messages ENABLE ROW LEVEL SECURITY;

-- Politiques de lecture publique
CREATE POLICY "Public Read Active Products" ON public.marketplace_products
    FOR SELECT USING (status = 'published' AND deleted_at IS NULL);

CREATE POLICY "Public Read Active Sellers" ON public.seller_profiles
    FOR SELECT USING (status = 'active');

-- Politiques d'accès bibliothèque acheteur
CREATE POLICY "Users Read Own Purchases" ON public.purchases
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users Read Own Orders" ON public.orders
    FOR SELECT USING (auth.uid() = buyer_user_id);

-- Politiques vendeurs sur leurs propres produits & gains
CREATE POLICY "Sellers Read Own Products" ON public.marketplace_products
    FOR ALL USING (seller_id IN (SELECT id FROM public.seller_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Sellers Read Own Payouts" ON public.seller_payouts
    FOR SELECT USING (seller_id IN (SELECT id FROM public.seller_profiles WHERE user_id = auth.uid()));

-- ============================================================================
-- 11. INITIAL SEED DATA (Catégories Officielles & Licences)
-- ============================================================================
INSERT INTO public.marketplace_categories (name, slug, description, icon, display_order)
VALUES
    ('Workflow Automation', 'workflow-automation', 'Automatisations n8n, Make.com et Zapier prêtes à l''emploi pour équipes B2B.', '⚡', 1),
    ('AI & Artificial Intelligence', 'ai-artificial-intelligence', 'Agents IA autonomes, pipelines LLM (Claude, OpenAI) et assistants voix.', '🤖', 2),
    ('Notion Templates', 'notion-templates', 'Systèmes de gestion de projet, operating systems et CRM complets pour Notion.', '📝', 3),
    ('Database & Backend', 'database-backend', 'Schémas PostgreSQL, configurations Supabase et tables Airtable prêtes pour la production.', '🗄️', 4),
    ('Productivity', 'productivity', 'Systèmes de productivité personnelle, dashboards exécutifs et trackers d''objectifs.', '⏱️', 5),
    ('Marketing Automation', 'marketing-automation', 'Génération de carrousels, scraping LinkedIn éthique et campagnes de prospection.', '📣', 6),
    ('Business & CRM', 'business-crm', 'Pipelines de vente, relances automatiques et intégrations Stripe/HubSpot.', '💼', 7),
    ('Developer Tools', 'developer-tools', 'Cursor Ruleset (.cursorrules), scripts Python de déploiement et templates d''API.', '🛠️', 8),
    ('SaaS Templates', 'saas-templates', 'Kits de démarrage Next.js, boilerplates multi-tenants et systèmes d''authentification.', '🚀', 9),
    ('No-Code & Low-Code', 'no-code-low-code', 'Architectures complètes prêtes à déployer sans écrire une seule ligne de code.', '🧩', 10)
ON CONFLICT (slug) DO NOTHING;

INSERT INTO public.product_licenses (license_key, title, description, allowed_domains_count, client_use_allowed, resale_allowed)
VALUES
    ('personal', 'Personal Use License', 'Utilisation autorisée sur 1 seul projet interne ou personnel. Revente ou distribution interdite.', 1, FALSE, FALSE),
    ('commercial', 'Commercial / Agency License', 'Déploiement illimité pour vous-même et pour vos clients B2B dans le cadre de vos prestations.', -1, TRUE, FALSE),
    ('extended', 'Extended SaaS License', 'Intégration directe dans une application SaaS commerciale distribuée à des tiers.', -1, TRUE, TRUE)
ON CONFLICT (license_key) DO NOTHING;
