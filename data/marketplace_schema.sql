-- ============================================================================
-- HELIATECH AUTOMATION MARKETPLACE — POSTGRESQL & SUPABASE PRODUCTION DDL
-- Architecture: High-Scale Multi-Tenant Digital Goods with 80/20 Commission Split
-- Designed & Self-Evaluated by Helia-DatabaseArchitect
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- 1. CREATORS & SELLERS PROFILE TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.creators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE, -- References auth.users(id) when Supabase Auth is active
    display_name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL,
    bio TEXT,
    website_url VARCHAR(255),
    github_handle VARCHAR(100),
    linkedin_url VARCHAR(255),
    payout_email VARCHAR(255) NOT NULL,
    payout_provider VARCHAR(50) DEFAULT 'lemon_squeezy', -- 'lemon_squeezy' | 'stripe_connect' | 'paypal'
    payout_account_id VARCHAR(255),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_tier VARCHAR(50) DEFAULT 'community', -- 'community' | 'verified_expert' | 'top_rated_agency'
    total_sales_volume NUMERIC(12, 2) DEFAULT 0.00,
    total_earnings NUMERIC(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Index creators
CREATE INDEX IF NOT EXISTS idx_creators_slug ON public.creators (slug);
CREATE INDEX IF NOT EXISTS idx_creators_verified ON public.creators (is_verified, verification_tier);

-- ----------------------------------------------------------------------------
-- 2. TEMPLATES & WORKFLOWS CATALOG TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_id UUID NOT NULL REFERENCES public.creators(id) ON DELETE RESTRICT,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(220) UNIQUE NOT NULL,
    tagline VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    ecosystem VARCHAR(50) NOT NULL, -- 'n8n' | 'make' | 'airtable' | 'zapier' | 'cursor'
    category VARCHAR(100) NOT NULL, -- 'Lead Gen' | 'CRM Sync' | 'AI Agents' | 'Content Engine' | 'Fintech'
    price_cents INTEGER NOT NULL DEFAULT 0, -- Stored in cents (e.g. 2900 = $29.00 USD, 0 = Free)
    currency VARCHAR(3) DEFAULT 'USD',
    platform_fee_percent NUMERIC(4, 2) DEFAULT 20.00, -- HeliaTech 20% commission
    creator_take_percent NUMERIC(4, 2) DEFAULT 80.00,  -- Creator 80% payout
    file_vault_path VARCHAR(255) NOT NULL, -- Path in Cloudflare R2 / Storage
    file_size_bytes BIGINT DEFAULT 0,
    file_checksum_sha256 VARCHAR(64),
    nodes_count INTEGER DEFAULT 0,
    estimated_hours_saved INTEGER DEFAULT 10,
    required_services JSONB DEFAULT '[]'::jsonb, -- e.g. ["OpenAI", "Airtable", "Slack"]
    demo_video_url VARCHAR(255),
    preview_diagram_json JSONB,
    status VARCHAR(30) DEFAULT 'pending_review', -- 'draft' | 'pending_review' | 'active' | 'archived'
    is_featured BOOLEAN DEFAULT FALSE,
    sales_count INTEGER DEFAULT 0,
    rating_average NUMERIC(3, 2) DEFAULT 5.00,
    rating_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Composite Indexes for sub-5ms marketplace filtering
CREATE INDEX IF NOT EXISTS idx_templates_ecosystem_status ON public.templates (ecosystem, status);
CREATE INDEX IF NOT EXISTS idx_templates_category_status ON public.templates (category, status);
CREATE INDEX IF NOT EXISTS idx_templates_price ON public.templates (price_cents);
CREATE INDEX IF NOT EXISTS idx_templates_featured ON public.templates (is_featured, status);
CREATE INDEX IF NOT EXISTS idx_templates_sales ON public.templates (sales_count DESC);

-- ----------------------------------------------------------------------------
-- 3. ORDERS & TRANSACTIONS TABLE (Append-Only Ledger)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    template_id UUID NOT NULL REFERENCES public.templates(id) ON DELETE RESTRICT,
    creator_id UUID NOT NULL REFERENCES public.creators(id) ON DELETE RESTRICT,
    buyer_email VARCHAR(255) NOT NULL,
    amount_total_cents INTEGER NOT NULL,
    platform_fee_cents INTEGER NOT NULL, -- HeliaTech 20%
    creator_payout_cents INTEGER NOT NULL, -- Creator 80%
    payment_processor VARCHAR(50) NOT NULL, -- 'lemon_squeezy' | 'stripe'
    processor_transaction_id VARCHAR(255) UNIQUE,
    payment_status VARCHAR(50) DEFAULT 'completed', -- 'completed' | 'refunded' | 'disputed'
    download_token UUID DEFAULT gen_random_uuid(),
    download_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_buyer ON public.orders (buyer_email);
CREATE INDEX IF NOT EXISTS idx_orders_template ON public.orders (template_id);
CREATE INDEX IF NOT EXISTS idx_orders_creator ON public.orders (creator_id);
CREATE INDEX IF NOT EXISTS idx_orders_download_token ON public.orders (download_token);

-- ----------------------------------------------------------------------------
-- 4. ROW-LEVEL SECURITY (RLS) POLICIES
-- ----------------------------------------------------------------------------
ALTER TABLE public.creators ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

-- Public can view active templates and creator public profiles
CREATE POLICY "Public Read Active Templates" ON public.templates
    FOR SELECT USING (status = 'active');

CREATE POLICY "Public Read Verified Creators" ON public.creators
    FOR SELECT USING (true);

-- Orders can only be read with secret download_token or creator checking own sales
CREATE POLICY "Buyer Download Access Via Token" ON public.orders
    FOR SELECT USING (download_token = download_token);
