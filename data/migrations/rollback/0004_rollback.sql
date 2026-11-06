-- ============================================================================
-- HeliaTech Sentinel Migration 0004 ROLLBACK PLAN
-- ============================================================================
PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS d1_usage_audit_log;
PRAGMA foreign_keys = ON;
