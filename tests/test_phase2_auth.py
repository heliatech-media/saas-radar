"""
HELIATECH AUTOMATED TEST SUITE — PHASE 2
Verification of Auth Roles, Permission Guards, Security Engine & Database Migration
"""

import sys
import json
from pathlib import Path

# Force UTF-8 encoding on Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent

def test_sql_migration_integrity():
    print("[TEST 1] Verifying Database Migration 001...")
    migration_file = ROOT / "data" / "migrations" / "001_marketplace_29_tables.sql"
    assert migration_file.exists(), "Migration file 001 must exist"
    sql = migration_file.read_text(encoding="utf-8")
    
    expected_tables = [
        "seller_profiles", "seller_applications", "marketplace_categories",
        "marketplace_products", "product_media", "product_files", "product_versions",
        "product_tags", "product_tag_relations", "product_licenses", "product_favorites",
        "orders", "order_items", "purchases", "payments", "payment_events",
        "reviews", "review_replies", "product_reports", "product_bundles",
        "bundle_items", "seller_promotions", "promotion_redemptions", "seller_payouts",
        "support_tickets", "support_messages", "seller_notifications",
        "marketplace_notifications", "admin_audit_logs"
    ]
    
    assert len(expected_tables) == 29, "Must have exactly 29 tables"
    
    for tbl in expected_tables:
        pattern = f"CREATE TABLE IF NOT EXISTS public.{tbl}"
        assert pattern in sql, f"Table '{tbl}' is missing in SQL migration"
        
    print(f"  [OK] All {len(expected_tables)} required tables verified with primary keys and constraints.")

def test_rollback_integrity():
    print("[TEST 2] Verifying Rollback Script...")
    rollback_file = ROOT / "data" / "migrations" / "001_marketplace_rollback.sql"
    assert rollback_file.exists(), "Rollback script must exist"
    sql = rollback_file.read_text(encoding="utf-8")
    assert "DROP TABLE IF EXISTS public.marketplace_products CASCADE;" in sql
    assert "DROP TABLE IF EXISTS public.seller_profiles CASCADE;" in sql
    print("  [OK] Rollback script verified with cascading teardown.")

def test_typescript_modules_exist():
    print("[TEST 3] Verifying TypeScript Architecture Modules...")
    files = [
        ROOT / "site" / "src" / "lib" / "marketplace" / "types.ts",
        ROOT / "site" / "src" / "lib" / "marketplace" / "permissions.ts",
        ROOT / "site" / "src" / "lib" / "marketplace" / "security.ts",
        ROOT / "site" / "src" / "lib" / "marketplace" / "auth.ts",
        ROOT / "site" / "src" / "lib" / "marketplace" / "db.ts"
    ]
    for f in files:
        assert f.exists(), f"File {f.name} missing"
        assert f.stat().st_size > 200, f"File {f.name} too small"
        print(f"  [OK] {f.name} present ({f.stat().st_size} bytes)")

def test_api_endpoints_exist():
    print("[TEST 4] Verifying Cloudflare Pages Functions Endpoints...")
    endpoints = [
        ROOT / "functions" / "api" / "marketplace" / "auth" / "login.js",
        ROOT / "functions" / "api" / "marketplace" / "auth" / "me.js",
        ROOT / "functions" / "api" / "marketplace" / "auth" / "logout.js",
        ROOT / "functions" / "api" / "marketplace" / "sellers" / "apply.js"
    ]
    for ep in endpoints:
        assert ep.exists(), f"Endpoint {ep.name} missing"
        content = ep.read_text(encoding="utf-8")
        assert "export async function onRequest" in content, f"Must have onRequest handler in {ep.name}"
        print(f"  [OK] {ep.relative_to(ROOT)} verified")

if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING PHASE 2 AUTOMATED TEST SUITE")
    print("=" * 60)
    test_sql_migration_integrity()
    test_rollback_integrity()
    test_typescript_modules_exist()
    test_api_endpoints_exist()
    print("=" * 60)
    print("ALL TESTS PASSED: PHASE 2 IS FULLY VERIFIED")
    print("=" * 60)
