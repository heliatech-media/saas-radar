-- ============================================================================
-- HeliaTech Sentinel Migration 0004 : Journal d'Audit Immuable avec Chaîne de Hash
-- ============================================================================
-- Table : d1_usage_audit_log (Interdiction applicative d'UPDATE et DELETE)
-- Chaîne de hash cryptographique SHA-256 liée séquentiellement (prev_hash -> entry_hash)

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS d1_usage_audit_log (
    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    actor_email TEXT NOT NULL,
    operation TEXT NOT NULL,          -- 'query' | 'execute' | 'export_r2' | 'probe'
    statement_type TEXT NOT NULL,     -- 'SELECT' | 'INSERT' | 'UPDATE' | 'DELETE' | 'MIGRATION'
    sanitized_sql TEXT NOT NULL,
    rows_affected INTEGER NOT NULL DEFAULT 0,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,             -- 'SUCCESS' | 'ERROR'
    error TEXT,
    token_scope TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    entry_hash TEXT NOT NULL          -- SHA-256(prev_hash + timestamp + actor + operation + sanitized_sql + status)
);

CREATE INDEX IF NOT EXISTS idx_d1_audit_seq ON d1_usage_audit_log(sequence_id);
CREATE INDEX IF NOT EXISTS idx_d1_audit_time ON d1_usage_audit_log(timestamp);
