-- ============================================================================
-- HeliaTech Sentinel V2 - Private Transactional Governance Schema
-- ============================================================================
-- Unified ACID relational tables for Cloudflare D1 and SQLite WAL.
-- Eradicates loose JSON operational and subscriber files.
-- Ensures strict audit logging, slot uniqueness, and human approval gates.

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. REGISTRE PRIVÉ DES ABONNÉS (Données Personnelles Chiffrées / Protégées)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subscribers (
    id TEXT PRIMARY KEY,                       -- sub_xxx ou UUIDv4
    email TEXT UNIQUE NOT NULL,                -- Toujours stocké en LOWER(TRIM(email))
    role TEXT,                                 -- Ex: "Director of Infrastructure"
    country TEXT,                              -- Ex: "United States"
    country_code TEXT,                         -- Ex: "US"
    signup_date TEXT NOT NULL,                 -- ISO 8601 UTC
    source_path TEXT,                          -- Ex: "/blog/make-vs-zapier"
    lead_magnet TEXT,                          -- Ex: "Make vs Zapier TCO Breakdown"
    status TEXT NOT NULL DEFAULT 'Verified',   -- Verified | Unsubscribed | Bounced
    last_engaged_at TEXT,                      -- Horodatage de dernière ouverture/clic
    unsubscribed_at TEXT                       -- Horodatage si désabonnement
);

CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status);
CREATE INDEX IF NOT EXISTS idx_subscribers_country ON subscribers(country_code);

-- ----------------------------------------------------------------------------
-- 2. ÉTAT DU CONTRÔLE DE LA FLOTTE (Ligne Unique ACID - id=1)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fleet_controls (
    id INTEGER PRIMARY KEY CHECK (id = 1),     -- Garantit strictement une seule ligne d'état
    fleet_status TEXT NOT NULL DEFAULT 'RUNNING', -- RUNNING | PAUSED
    newsletter_emergency_stop INTEGER NOT NULL DEFAULT 0, -- 0: Actif, 1: Gelé immédiatement
    suspended_agents TEXT NOT NULL DEFAULT '[]', -- JSON Array des agents suspendus manuellement
    exempt_agents TEXT NOT NULL DEFAULT '["SecurityAgent","MarketplaceSecuritySentinel","NotifierAgent"]', -- Non-suspensibles
    last_updated_at TEXT NOT NULL,
    last_updated_by TEXT NOT NULL
);

-- Initialisation garantie de la ligne unique
INSERT OR IGNORE INTO fleet_controls (id, fleet_status, newsletter_emergency_stop, suspended_agents, exempt_agents, last_updated_at, last_updated_by)
VALUES (1, 'RUNNING', 0, '[]', '["SecurityAgent","MarketplaceSecuritySentinel","NotifierAgent"]', datetime('now'), 'system_init');

-- ----------------------------------------------------------------------------
-- 3. FILE D'ATTENTE D'APPROBATION PATRON (Human-in-the-Loop Obligatoire)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS owner_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL,                   -- 'newsletter_edition' | 'article' | 'score_change' | 'deal_update'
    item_ref TEXT NOT NULL,                    -- Ex: slot_key '2026-11-12:thursday' ou slug
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    content_payload TEXT NOT NULL,             -- JSON normalisé ou HTML de l'élément
    content_hash TEXT NOT NULL,                -- SHA-256 du contenu
    author_agent TEXT NOT NULL,                -- Ex: "NewsletterEngine" ou "ContentWriter"
    status TEXT NOT NULL DEFAULT 'PENDING',    -- PENDING | APPROVED | REJECTED | CANCELLED
    created_at TEXT NOT NULL,
    decided_at TEXT,
    decided_by TEXT,
    decision_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_approvals_status ON owner_approvals(status);
CREATE INDEX IF NOT EXISTS idx_approvals_item_ref ON owner_approvals(item_ref);

-- ----------------------------------------------------------------------------
-- 4. JOURNAL D'AUDIT IMMUABLE (Append-Only avec Preuve Cryptographique)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sentinel_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,                   -- ISO 8601 UTC
    actor_email TEXT NOT NULL,                 -- Email authentifié par Cloudflare Zero Trust
    actor_role TEXT NOT NULL DEFAULT 'owner',  -- 'owner' obligatoire pour les actions critiques
    action TEXT NOT NULL,                      -- PAUSE_ALL_AGENTS | STOP_NEWSLETTER | APPROVE_ITEM | etc.
    target TEXT NOT NULL,                      -- 'fleet' | 'newsletter' | 'agent:<name>' | 'approval:<id>'
    details_json TEXT NOT NULL,                -- Payload complet avant/après
    previous_state TEXT,
    new_state TEXT,
    ip_address TEXT,
    user_agent TEXT,
    signature TEXT NOT NULL                    -- SHA-256(id + timestamp + actor + action + new_state + prev_signature)
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON sentinel_audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_action ON sentinel_audit_logs(action);

-- ----------------------------------------------------------------------------
-- 5. ÉDITIONS & DISPATCHS NEWSLETTER (Unicité des Créneaux ACID)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS newsletter_editions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_key TEXT UNIQUE NOT NULL,             -- Ex: "2026-11-12:thursday"
    scheduled_date TEXT NOT NULL,              -- "2026-11-12"
    edition_type TEXT NOT NULL,                -- "thursday" | "tuesday"
    status TEXT NOT NULL,                      -- 'draft' | 'validated' | 'dispatched' | 'cancelled'
    issue_number INTEGER UNIQUE,               -- 55
    subject TEXT NOT NULL,
    normalized_subject TEXT NOT NULL,
    content_html TEXT NOT NULL,
    content_hash TEXT NOT NULL,                -- SHA-256
    selected_items TEXT NOT NULL,              -- JSON Array des IDs inclus
    rejection_reason TEXT,
    recipients_total INTEGER DEFAULT 0,
    recipients_sent INTEGER DEFAULT 0,
    recipients_ignored INTEGER DEFAULT 0,
    duplicates_blocked INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    validated_at TEXT,
    dispatched_at TEXT,
    UNIQUE(scheduled_date, edition_type)
);

CREATE TABLE IF NOT EXISTS newsletter_dispatches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_key TEXT NOT NULL,
    subscriber_id TEXT NOT NULL,
    subscriber_email TEXT NOT NULL,
    issue_number INTEGER NOT NULL,
    dispatched_at TEXT NOT NULL,
    resend_id TEXT,
    status TEXT NOT NULL,
    UNIQUE(slot_key, subscriber_id),
    UNIQUE(slot_key, subscriber_email),
    FOREIGN KEY(slot_key) REFERENCES newsletter_editions(slot_key)
);
