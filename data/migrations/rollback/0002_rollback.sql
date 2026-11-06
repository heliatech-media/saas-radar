-- ============================================================================
-- HeliaTech Sentinel Migration 0002 ROLLBACK PLAN
-- ============================================================================
PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS versus_matrix;
DROP TABLE IF EXISTS content_inventory;
DROP TABLE IF EXISTS deals_registry;
PRAGMA foreign_keys = ON;
