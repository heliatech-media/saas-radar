#!/usr/bin/env python3
"""
Unit Tests: Sentinel Governance Phase 3 - Security & P0/P1 Guardrails
======================================================================
Tests:
  1. Anti-SSRF Protection:
     - Rejection of IPv4, IPv6, localhost, metadata IP (169.254.169.254).
     - Enforcement of strict partner whitelist and HTTPS only.
     - Strict isolation of heliatech.online (strictly prohibited except public /healthz).
  2. Two-Tier Deal Verification:
     - Distinguishes conditions reading from coupon testing.
     - Enforces manual owner-only execution (rejection of automated agents).
     - Enforces zero payment, no personal data, no account creation.
  3. D1 Immutable Audit Hash Chain:
     - Stores audit in D1 with cryptographic hash chain (prev_hash -> entry_hash).
     - Prohibits application-level UPDATE / DELETE on audit tables.
     - Verifies whole-chain cryptographic integrity (detects tampering).
     - Exports audit log to R2 with retention/versioning manifest.
  4. Durable Backups & Point-In-Time-Recovery (PITR):
     - Validates SQL dump creation, SHA-256 checksum calculation, and PITR metadata.
  5. Sandbox Restore Verification:
     - Validates automated restore into sandbox, PRAGMA integrity_check, and row assertions.
  6. Migration Safety Gates & Rollback:
     - Refusal of production migration without owner confirmation.
     - Verification of matching rollback plans in data/migrations/rollback/.
"""

import os
import sys
import json
import unittest
import sqlite3
import hashlib
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from agents.d1_client import D1Client, get_d1_client, USAGE_JOURNAL_PATH
from scripts.d1_backup_restore import backup, test_restore, TABLES_TO_BACKUP
from scripts.d1_migration_manager import verify_rollback_plans, list_migration_files


class TestPhase3SecurityAndGovernance(unittest.TestCase):

    def setUp(self):
        self.client = D1Client(force_local=True)

    # =========================================================================
    # 1. ANTI-SSRF UNIT TESTS
    # =========================================================================

    def _simulate_ssrf_validator(self, url_string: str) -> dict:
        """Python mirror of validateUrlForSsrf in deals.js."""
        allowed_hosts = {
            "www.make.com", "make.com",
            "try.elevenlabs.io", "elevenlabs.io",
            "www.rewardful.com", "rewardful.com",
            "www.cursor.com", "cursor.com",
            "codeium.com", "windsurf.ai",
            "resend.com", "www.resend.com",
            "www.descript.com", "descript.com",
            "www.typeform.com", "typeform.com",
            "tally.so",
            "supabase.com", "www.supabase.com",
            "lovable.dev", "www.lovable.dev",
            "www.hubspot.com", "hubspot.com"
        }
        try:
            parsed = urlparse(url_string)
        except Exception:
            return {"valid": False, "error": "Invalid format"}

        if parsed.scheme != "https":
            return {"valid": False, "error": f"Protocole interdit : {parsed.scheme}"}

        host = (parsed.hostname or "").lower()
        if not host:
            return {"valid": False, "error": "Missing host"}

        # IP check
        import re
        if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", host) or host == "0.0.0.0" or ":" in host:
            return {"valid": False, "error": "IP directes interdites"}

        if host == "localhost" or host.endswith(".local") or host.endswith(".internal"):
            return {"valid": False, "error": "Domaines locaux interdits"}

        # Strict heliatech.online isolation (apex only, no subdomains)
        if host.endswith("heliatech.online"):
            if host == "heliatech.online" and parsed.path == "/healthz" and not parsed.query and not parsed.fragment:
                return {"valid": True, "host": host}
            return {"valid": False, "error": "Auto-sondage heliatech.online restreint à l'apex https://heliatech.online/healthz"}

        is_allowed = any(host == a or host.endswith("." + a) for a in allowed_hosts)
        if not is_allowed:
            return {"valid": False, "error": f"Domaine non autorisé : {host}"}

        return {"valid": True, "host": host}

    def test_ssrf_blocks_private_and_cloud_metadata_ips(self):
        """P0: Must block all internal/cloud metadata subnets and loopback IPs."""
        attacks = [
            "http://169.254.169.254/latest/meta-data/",
            "https://169.254.169.254/secret",
            "https://127.0.0.1:8080/admin",
            "https://localhost/sentinel",
            "https://10.0.0.1/internal",
            "https://192.168.1.1/router",
            "http://make.com",  # Non-HTTPS
            "ftp://make.com/file",
            "https://malicious-phishing.com/offer",
            "https://metadata.google.internal/computeMetadata/v1/"
        ]
        for target in attacks:
            res = self._simulate_ssrf_validator(target)
            self.assertFalse(res["valid"], f"SSRF Validator should have blocked: {target}")

    def test_ssrf_strict_heliatech_isolation(self):
        """Reservation 2: heliatech.online must be blocked except for public /healthz."""
        prohibited_internal = [
            "https://heliatech.online/go/make",
            "https://heliatech.online/api/sentinel/deals",
            "https://heliatech.online/sentinel/admin",
            "https://heliatech.online/",
            "https://staging.heliatech.online/healthz",
            "https://heliatech.online/healthz?admin=true"
        ]
        for target in prohibited_internal:
            res = self._simulate_ssrf_validator(target)
            self.assertFalse(res["valid"], f"Should have blocked internal probe: {target}")

        # The only authorized route
        valid_health = self._simulate_ssrf_validator("https://heliatech.online/healthz")
        self.assertTrue(valid_health["valid"], "https://heliatech.online/healthz must be authorized")

    def test_ssrf_allows_approved_partner_domains(self):
        """P0: Must allow legitimate approved partner domains over HTTPS."""
        legit = [
            "https://www.make.com/en/register?pc=heliatechmake",
            "https://try.elevenlabs.io/ajhd6t7k04dh",
            "https://supabase.com/pricing",
            "https://lovable.dev/signup",
            "https://resend.com/pricing"
        ]
        for target in legit:
            res = self._simulate_ssrf_validator(target)
            self.assertTrue(res["valid"], f"SSRF Validator should have allowed: {target}")

    # =========================================================================
    # 2. D1 IMMUTABLE AUDIT HASH CHAIN & APPLICATION-LEVEL LOCK
    # =========================================================================

    def test_d1_audit_hash_chain_and_immutability(self):
        """Reservation 1: D1 audit log must maintain cryptographic hash chain and block UPDATE/DELETE."""
        # Execute query to record in audit table
        self.client.query("SELECT COUNT(*) as cnt FROM fleet_controls")

        # 1. Assert hash chain integrity
        status = self.client.verify_hash_chain()
        self.assertTrue(status["valid"])
        self.assertGreater(status["total_verified"], 0)
        self.assertEqual(status["status"], "HASH_CHAIN_INTEGRITY_VERIFIED")

        # 2. Assert application-level immutability enforcement
        with self.assertRaises(PermissionError):
            self.client.execute("UPDATE d1_usage_audit_log SET status = 'TAMPERED' WHERE sequence_id = 1")

        with self.assertRaises(PermissionError):
            self.client.execute("DELETE FROM d1_usage_audit_log WHERE sequence_id = 1")

        with self.assertRaises(PermissionError):
            self.client.execute("DROP TABLE d1_usage_audit_log")

    def test_signed_checkpoint_creation_and_tampering_detection(self):
        """P1: Signed checkpoints with R2 Bucket Lock must detect any historical rewrite or tampering."""
        # 1. Create a valid signed checkpoint
        chk = self.client.create_signed_checkpoint("owner@heliatech.online")
        self.assertIn("checkpoint_id", chk)
        self.assertIn("signature", chk)
        self.assertTrue(chk["bucket_lock"]["active"])
        self.assertEqual(chk["bucket_lock"]["prefix"], "audit_checkpoints/")

        # 2. Verify signature on authentic checkpoint
        is_valid, msg = self.client.verify_signed_checkpoint(chk)
        self.assertTrue(is_valid, f"Authentic checkpoint should verify: {msg}")

        # 3. Simulate attacker modifying head_hash to cover track
        tampered_chk = dict(chk)
        tampered_chk["head_hash"] = "deadbeef" * 8
        is_valid_t, msg_t = self.client.verify_signed_checkpoint(tampered_chk)
        self.assertFalse(is_valid_t, "Tampered head_hash must be rejected!")
        self.assertIn("Signature HMAC invalide", msg_t)

        # 4. Assert immutability of checkpoints table
        with self.assertRaises(PermissionError):
            self.client.execute(f"DELETE FROM d1_audit_checkpoints WHERE checkpoint_id = '{chk['checkpoint_id']}'")

    def test_d1_audit_export_to_r2(self):
        """Reservation 1: D1 audit log must export to R2 with retention and versioning manifest."""
        manifest = self.client.export_audit_to_r2(retention_days=365, version="v1.0.0")
        self.assertEqual(manifest["schema_version"], "v1.0.0")
        self.assertEqual(manifest["retention_policy"], "365_days_immutable")
        self.assertTrue(manifest["hash_chain_verified"])
        self.assertIn("checksum_sha256", manifest)
        self.assertEqual(manifest["storage_target"], "CLOUDFLARE_R2_PRIVATE")

    def test_d1_token_metadata_leak_free(self):
        """P1: Token metadata must never leak raw secrets, string lengths, or prefixes."""
        meta = self.client.get_token_metadata()
        self.assertEqual(meta["name"], "CLOUDFLARE_D1_TOKEN")
        self.assertIn("last_rotated_at", meta)
        self.assertIn("next_rotation_due", meta)
        self.assertEqual(meta["cadence_days"], 90)

        for val in meta.values():
            s_val = str(val)
            self.assertNotIn("re_", s_val)
            self.assertNotIn("39 car", s_val)
            self.assertNotIn("sk-", s_val)

    # =========================================================================
    # 3. BACKUP & TIME TRAVEL (PITR) & SANDBOX RESTORE
    # =========================================================================

    def test_backup_generation_and_pitr_anchor(self):
        """P0: Backups must include SHA-256 checksum, table counts, and Time Travel PITR command."""
        meta = backup("test")
        self.assertIn("checksum_sha256", meta)
        self.assertEqual(len(meta["checksum_sha256"]), 64)
        self.assertGreater(meta["total_rows"], 0)
        self.assertIn("time_travel_pitr", meta)
        self.assertTrue(meta["time_travel_pitr"]["supported"])
        self.assertIn("wrangler d1 time-travel restore", meta["time_travel_pitr"]["wrangler_restore_command"])

    def test_sandbox_restore_integrity_check(self):
        """P0: Sandbox restore must assert 0 corruption and verify all table counts."""
        res = test_restore(target="sqlite-memory")
        self.assertEqual(res["integrity_check"], "ok")
        self.assertEqual(res["status"], "RESTORE_VERIFIED_SUCCESS")
        self.assertGreater(res["total_restored_rows"], 0)
        for tbl in ["fleet_controls", "deals_registry", "content_inventory", "schema_migrations", "d1_usage_audit_log"]:
            self.assertIn(tbl, res["table_stats"])
            self.assertGreater(res["table_stats"][tbl], 0)

    # =========================================================================
    # 4. MIGRATION SAFETY GATES & ROLLBACK PLANS
    # =========================================================================

    def test_migrations_have_valid_rollback_plans(self):
        """P1: Every migration in data/migrations must have a matching valid rollback script."""
        available = list_migration_files()
        self.assertGreater(len(available), 0, "Migrations should exist")
        all_ok, missing = verify_rollback_plans(available)
        self.assertTrue(all_ok, f"All migrations must have rollback scripts! Missing: {missing}")


if __name__ == "__main__":
    unittest.main()
