# -*- coding: utf-8 -*-
"""
Phase 6 Verification Test Suite — Admin Dashboard
Validates:
1. Admin backend API endpoints (overview, moderation, sellers, payouts, audit_logs)
2. Astro static build artifact verification for /admin/marketplace/
3. Moderation queue, seller accreditation, and audit logging presence
"""
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def test_admin_api_endpoints():
    print(">>> Testing Admin API endpoints...")
    expected_endpoints = [
        "functions/api/marketplace/admin/overview.js",
        "functions/api/marketplace/admin/moderation.js",
        "functions/api/marketplace/admin/sellers.js",
        "functions/api/marketplace/admin/payouts.js",
        "functions/api/marketplace/admin/audit_logs.js",
        "site/functions/api/marketplace/admin/overview.js",
        "site/functions/api/marketplace/admin/moderation.js",
        "site/functions/api/marketplace/admin/sellers.js",
        "site/functions/api/marketplace/admin/payouts.js",
        "site/functions/api/marketplace/admin/audit_logs.js"
    ]

    for fpath in expected_endpoints:
        assert os.path.exists(fpath), f"Missing admin API endpoint file: {fpath}"
        content = open(fpath, "r", encoding="utf-8").read()
        assert len(content) > 50, f"File {fpath} appears empty"

    print(f"  [OK] All {len(expected_endpoints)} Admin API endpoint files verified.")

def test_admin_marketplace_html():
    print(">>> Testing Astro static build output in site/dist/admin/marketplace/...")
    dist_file = "site/dist/admin/marketplace/index.html"
    assert os.path.exists(dist_file), f"Missing {dist_file}"

    content = open(dist_file, "r", encoding="utf-8").read()

    # Check key features
    assert "Console d'Administration" in content or "Supervision Marketplace" in content, "Missing Admin Console title"
    assert "Volume Brut (GMV)" in content or "GMV" in content, "Missing GMV metric"
    assert "Modération" in content, "Missing Moderation section"
    assert "Candidatures" in content or "Vendeurs" in content, "Missing Sellers section"
    assert "Versements" in content or "Payouts" in content, "Missing Payouts section"
    assert "Journal d'Audit" in content, "Missing Audit Logs section"

    print("  [OK] /admin/marketplace/index.html contains all administrative modules.")

def main():
    print("=== RUNNING PHASE 6 TEST SUITE (ADMIN DASHBOARD) ===")
    test_admin_api_endpoints()
    test_admin_marketplace_html()
    print("=== ALL PHASE 6 TESTS PASSED PERFECTLY ===")

if __name__ == "__main__":
    main()
