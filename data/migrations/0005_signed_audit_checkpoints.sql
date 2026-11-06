-- ============================================================================
-- HeliaTech Sentinel Migration 0005 : Points de Contrôle d'Audit Signés (R2 Lock)
-- ============================================================================
-- Table : d1_audit_checkpoints
-- Ancre cryptographique externe signée (HMAC/Ed25519) découplée du token D1,
-- exportée vers Cloudflare R2 sous préfixe immuable protégé par Bucket Lock (WORM).

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS d1_audit_checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    sequence_id INTEGER NOT NULL,
    head_hash TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    total_records INTEGER NOT NULL,
    signing_key_id TEXT NOT NULL,
    signature TEXT NOT NULL,
    r2_prefix TEXT NOT NULL DEFAULT 'audit_checkpoints/',
    r2_bucket TEXT NOT NULL DEFAULT 'heliatech-sentinel-backups',
    bucket_lock_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_checkpoint_seq ON d1_audit_checkpoints(sequence_id);
CREATE INDEX IF NOT EXISTS idx_checkpoint_time ON d1_audit_checkpoints(timestamp);
