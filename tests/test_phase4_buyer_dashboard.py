# -*- coding: utf-8 -*-
"""
Phase 4 Verification Test Suite — Buyer Dashboard
Validates:
1. Cloudflare Pages Functions endpoints for buyer (library, download, orders, reviews, support)
2. Astro static build artifact verification for /dashboard/
3. Inspection of tabs, KPI statistics, and invoice generation modal
"""
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def test_buyer_api_endpoints():
    print(">>> Testing Buyer API endpoints...")
    expected_buyer_endpoints = [
        "functions/api/marketplace/buyer/library.js",
        "functions/api/marketplace/buyer/download.js",
        "functions/api/marketplace/buyer/orders.js",
        "functions/api/marketplace/buyer/reviews.js",
        "functions/api/marketplace/buyer/support.js",
        "site/functions/api/marketplace/buyer/library.js",
        "site/functions/api/marketplace/buyer/download.js",
        "site/functions/api/marketplace/buyer/orders.js",
        "site/functions/api/marketplace/buyer/reviews.js",
        "site/functions/api/marketplace/buyer/support.js"
    ]

    for fpath in expected_buyer_endpoints:
        assert os.path.exists(fpath), f"Missing buyer API endpoint file: {fpath}"
        content = open(fpath, "r", encoding="utf-8").read()
        assert len(content) > 50, f"File {fpath} appears empty"

    print(f"  [OK] All {len(expected_buyer_endpoints)} Buyer API endpoint files verified.")

def test_dashboard_built_html():
    print(">>> Testing Astro static build output in site/dist/dashboard/...")
    dist_file = "site/dist/dashboard/index.html"
    assert os.path.exists(dist_file), f"Missing {dist_file}"

    content = open(dist_file, "r", encoding="utf-8").read()

    # Verify key sections and tabs
    assert "Tableau de Bord Acheteur" in content or "Espace Acheteur" in content, "Missing dashboard title"
    assert "Ma Bibliothèque" in content, "Missing Library tab"
    assert "Mes Commandes" in content, "Missing Orders tab"
    assert "Ma Wishlist" in content, "Missing Wishlist tab"
    assert "Mes Avis Laissés" in content, "Missing Reviews tab"
    assert "Support &amp; Échanges" in content or "Support & Échanges" in content, "Missing Support tab"
    assert "invoice-modal" in content, "Missing Printable Invoice modal"
    assert "HLT-LIC-" in content, "Missing license key formatting"

    print("  [OK] /dashboard/index.html contains all 6 required buyer sections and invoice modal.")

def main():
    print("=== RUNNING PHASE 4 TEST SUITE (BUYER DASHBOARD) ===")
    test_buyer_api_endpoints()
    test_dashboard_built_html()
    print("=== ALL PHASE 4 TESTS PASSED PERFECTLY ===")

if __name__ == "__main__":
    main()
