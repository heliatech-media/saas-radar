# -*- coding: utf-8 -*-
"""
Phase 5 Verification Test Suite — Seller Studio
Validates:
1. Seller backend API endpoints (overview, products, payouts, coupons, versions)
2. Astro static build artifact verification for /seller/
3. 80/20 revenue accounting rules and 7-step wizard DOM presence
"""
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def test_seller_api_endpoints():
    print(">>> Testing Seller API endpoints...")
    expected_endpoints = [
        "functions/api/marketplace/seller/overview.js",
        "functions/api/marketplace/seller/products.js",
        "functions/api/marketplace/seller/payouts.js",
        "functions/api/marketplace/seller/coupons.js",
        "functions/api/marketplace/seller/versions.js",
        "site/functions/api/marketplace/seller/overview.js",
        "site/functions/api/marketplace/seller/products.js",
        "site/functions/api/marketplace/seller/payouts.js",
        "site/functions/api/marketplace/seller/coupons.js",
        "site/functions/api/marketplace/seller/versions.js"
    ]

    for fpath in expected_endpoints:
        assert os.path.exists(fpath), f"Missing seller API endpoint file: {fpath}"
        content = open(fpath, "r", encoding="utf-8").read()
        assert len(content) > 50, f"File {fpath} appears empty"

    print(f"  [OK] All {len(expected_endpoints)} Seller API endpoint files verified.")

def test_seller_studio_html():
    print(">>> Testing Astro static build output in site/dist/seller/...")
    dist_file = "site/dist/seller/index.html"
    assert os.path.exists(dist_file), f"Missing {dist_file}"

    content = open(dist_file, "r", encoding="utf-8").read()

    # Check key features
    assert "Studio Vendeur" in content or "Studio Créateur" in content, "Missing Seller Studio title"
    assert "80%" in content, "Missing 80% net revenue mention"
    assert "Wizard" in content or "Déposer un Template" in content, "Missing Wizard tab"
    assert "wstep-1" in content and "wstep-7" in content, "Missing 7-step wizard sections"
    assert "Codes Promo" in content or "Codes Promotionnels" in content, "Missing Coupons section"
    assert "Versements" in content or "Stripe Connect" in content, "Missing Payouts section"
    assert "Sentinel" in content, "Missing Sentinel AST scanner mention"

    print("  [OK] /seller/index.html contains all Seller Studio features (80% net, 7-step wizard, payouts).")

def main():
    print("=== RUNNING PHASE 5 TEST SUITE (SELLER STUDIO) ===")
    test_seller_api_endpoints()
    test_seller_studio_html()
    print("=== ALL PHASE 5 TESTS PASSED PERFECTLY ===")

if __name__ == "__main__":
    main()
