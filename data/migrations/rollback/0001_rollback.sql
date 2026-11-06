-- ============================================================================
-- HeliaTech Sentinel Migration 0001 ROLLBACK PLAN
-- ============================================================================
PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS newsletter_dispatches;
DROP TABLE IF EXISTS newsletter_editions;
DROP TABLE IF EXISTS sentinel_audit_logs;
DROP TABLE IF EXISTS owner_approvals;
DROP TABLE IF EXISTS fleet_controls;
DROP TABLE IF EXISTS subscribers;
PRAGMA foreign_keys = ON;
