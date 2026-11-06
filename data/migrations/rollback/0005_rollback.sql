-- ============================================================================
-- HeliaTech Sentinel Migration 0005 ROLLBACK PLAN
-- ============================================================================
PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS d1_audit_checkpoints;
PRAGMA foreign_keys = ON;
