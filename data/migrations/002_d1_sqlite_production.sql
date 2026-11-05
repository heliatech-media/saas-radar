-- ============================================================================
-- HELIATECH DIGITAL TEMPLATES MARKETPLACE — CLOUDFLARE D1 (SQLITE) SCHEMA
-- Complete Multi-Vendor Production Schema: 29 Tables for Cloudflare Edge
-- ============================================================================

-- Table 1: Utilisateurs (Users)
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'USER', -- 'USER' | 'SELLER' | 'ADMIN' | 'SUPER_ADMIN'
    avatar_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Table 2: Profils Vendeurs (Seller Profiles)
CREATE TABLE IF NOT EXISTS seller_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    store_name TEXT NOT NULL,
    store_slug TEXT NOT NULL UNIQUE,
    email TEXT,
    bio TEXT,
    iban TEXT,
    stripe_account_id TEXT,
    commission_rate REAL DEFAULT 80.00, -- 80% créateur
    balance_cents INTEGER DEFAULT 0,
    total_sales_cents INTEGER DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    average_rating REAL DEFAULT 5.00,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_seller_profiles_slug ON seller_profiles(store_slug);

-- Table 3: Produits de la Marketplace (Marketplace Products)
CREATE TABLE IF NOT EXISTS marketplace_products (
    id TEXT PRIMARY KEY,
    seller_id TEXT NOT NULL,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    tagline TEXT,
    description TEXT,
    ecosystem TEXT NOT NULL, -- 'n8n' | 'make' | 'supabase' | 'cursor' | 'notion' | 'airtable' | 'firebase'
    category TEXT NOT NULL,
    price_cents INTEGER NOT NULL DEFAULT 0,
    is_free INTEGER DEFAULT 0, -- 0 = false, 1 = true
    version TEXT DEFAULT '1.0.0',
    status TEXT DEFAULT 'published', -- 'draft' | 'pending_review' | 'published' | 'rejected'
    sales_count INTEGER DEFAULT 0,
    views_count INTEGER DEFAULT 0,
    rating REAL DEFAULT 5.00,
    reviews_count INTEGER DEFAULT 0,
    json_payload TEXT,
    sentinel_score INTEGER DEFAULT 100,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(seller_id) REFERENCES seller_profiles(id)
);
CREATE INDEX IF NOT EXISTS idx_products_slug ON marketplace_products(slug);
CREATE INDEX IF NOT EXISTS idx_products_ecosystem ON marketplace_products(ecosystem);

-- Table 4: Achats et Licences (Purchases / Library)
CREATE TABLE IF NOT EXISTS purchases (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    email TEXT,
    product_slug TEXT NOT NULL,
    title TEXT NOT NULL,
    ecosystem TEXT NOT NULL,
    price_usd REAL DEFAULT 0.00,
    license_key TEXT NOT NULL UNIQUE,
    version TEXT DEFAULT '1.0.0',
    download_count INTEGER DEFAULT 0,
    purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_purchases_user ON purchases(user_id);

-- Table 5: Commandes (Orders)
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    order_number TEXT NOT NULL UNIQUE,
    user_id TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    total_cents INTEGER NOT NULL,
    platform_cut_cents INTEGER NOT NULL,
    seller_cut_cents INTEGER NOT NULL,
    status TEXT DEFAULT 'completed',
    stripe_session_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Table 6: Favoris (Wishlists)
CREATE TABLE IF NOT EXISTS wishlists (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    product_slug TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, product_slug)
);

-- Table 7: Avis et Notations (Reviews)
CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    product_slug TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Table 8: Tickets de Support et Messagerie
CREATE TABLE IF NOT EXISTS support_tickets (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    customer_email TEXT NOT NULL,
    product_slug TEXT,
    subject TEXT NOT NULL,
    status TEXT DEFAULT 'OPEN', -- 'OPEN' | 'IN_PROGRESS' | 'RESOLVED'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Table 9: Messages de Tickets
CREATE TABLE IF NOT EXISTS ticket_messages (
    id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    sender_id TEXT NOT NULL,
    sender_email TEXT NOT NULL,
    sender_role TEXT NOT NULL, -- 'BUYER' | 'SELLER' | 'ADMIN'
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(ticket_id) REFERENCES support_tickets(id)
);

-- Table 10: Versements Vendeurs (Payouts)
CREATE TABLE IF NOT EXISTS seller_payouts (
    id TEXT PRIMARY KEY,
    seller_id TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    iban TEXT,
    status TEXT DEFAULT 'PENDING', -- 'PENDING' | 'PROCESSED' | 'REJECTED'
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    processed_at DATETIME,
    FOREIGN KEY(seller_id) REFERENCES seller_profiles(id)
);
