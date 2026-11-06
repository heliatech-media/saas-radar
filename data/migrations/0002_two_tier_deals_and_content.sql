-- ============================================================================
-- HeliaTech Sentinel Migration 0002 : Deux Niveaux Deals & Preuves Contenus
-- ============================================================================
-- Tables : deals_registry (séparation LINK_REACHABLE / OFFER_VERIFIED), content_inventory, versus_matrix

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS deals_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL,
    tool_slug TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    partner_code TEXT,
    perk_title TEXT NOT NULL,
    badge TEXT NOT NULL,
    affiliate_url TEXT NOT NULL,
    savings_estimate TEXT NOT NULL,
    verification_cadence_hours INTEGER NOT NULL DEFAULT 48,
    proof_url TEXT,
    -- 1. Disponibilité Technique du Lien (Sondage HTTP HEAD/GET)
    link_status TEXT NOT NULL DEFAULT 'LINK_REACHABLE', -- LINK_REACHABLE | LINK_BROKEN | UNCHECKED
    link_checked_at TEXT NOT NULL,                      -- Horodatage du dernier ping HTTP
    link_http_code INTEGER NOT NULL DEFAULT 200,        -- Code retour (200, 302, 404, etc.)
    link_latency_ms INTEGER NOT NULL DEFAULT 120,       -- Temps de réponse réseau
    -- 2. Validité Commerciale de l'Offre (Audit Contrat / Code Promo / Conditions)
    offer_status TEXT NOT NULL DEFAULT 'OFFER_VERIFIED',-- OFFER_VERIFIED | OFFER_EXPIRED | PENDING_HUMAN_CHECK
    offer_verified_at TEXT NOT NULL,                    -- Horodatage de validation par l'Owner
    offer_verified_by TEXT NOT NULL DEFAULT 'owner',    -- 'owner' ou 'editorial_audit'
    offer_terms_notes TEXT,                             -- Preuve : code promo actif, conditions testées
    verified_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);

CREATE INDEX IF NOT EXISTS idx_deals_status ON deals_registry(status);

CREATE TABLE IF NOT EXISTS content_inventory (
    slug TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    word_count INTEGER NOT NULL DEFAULT 0,
    evidence_count INTEGER NOT NULL DEFAULT 3,
    tco_accuracy_score REAL NOT NULL DEFAULT 9.0,
    audit_status TEXT NOT NULL DEFAULT 'VERIFIED',
    last_audited_at TEXT NOT NULL,
    verified_by TEXT NOT NULL DEFAULT 'DataVerifier'
);

CREATE INDEX IF NOT EXISTS idx_content_status ON content_inventory(audit_status);

CREATE TABLE IF NOT EXISTS versus_matrix (
    duel_slug TEXT PRIMARY KEY,
    tool_a TEXT NOT NULL,
    tool_b TEXT NOT NULL,
    winner_tool TEXT,
    category TEXT NOT NULL,
    tco_delta TEXT NOT NULL,
    last_benchmarked_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);
