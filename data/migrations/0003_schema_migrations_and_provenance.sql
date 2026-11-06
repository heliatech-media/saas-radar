-- ============================================================================
-- HeliaTech Sentinel Migration 0003 : Journalisation des Migrations & Sourcing
-- ============================================================================
-- Table : schema_migrations (traçabilité test / preprod / prod)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    environment TEXT NOT NULL,            -- 'test' | 'preprod' | 'prod'
    applied_at TEXT NOT NULL,             -- ISO 8601 UTC
    checksum TEXT NOT NULL,               -- SHA-256 du fichier SQL
    applied_by TEXT NOT NULL              -- 'owner' ou runner id
);

CREATE INDEX IF NOT EXISTS idx_migrations_env ON schema_migrations(environment);

-- Initialisation des versions appliquées
INSERT OR IGNORE INTO schema_migrations (version, name, environment, applied_at, checksum, applied_by)
VALUES 
    (1, '0001_initial_sentinel_schema.sql', 'prod', datetime('now'), 'sha256_init_schema', 'owner'),
    (2, '0002_two_tier_deals_and_content.sql', 'prod', datetime('now'), 'sha256_deals_content', 'owner'),
    (3, '0003_schema_migrations_and_provenance.sql', 'prod', datetime('now'), 'sha256_migrations_provenance', 'owner');
