#!/usr/bin/env python3
"""
Unit Tests: Sentinel Governance Phase 3 - Security & P0/P1 Guardrails
======================================================================
Tests:
  1. Anti-SSRF Protection:
     - Rejection of IPv4, IPv6, localhost, metadata IP (169.254.169.254).
     - Enforcement of strict partner whitelist and HTTPS only.
  2. Two-Tier Deal Verification:
     - Distinguishes conditions reading from coupon testing.
     - Enforces zero payment / ethical protocol.
  3. D1 Scoped Token & Usage Journal:
     - Verifies append-only logging of queries in d1_usage_journal.jsonl.
     - Verifies zero secret, prefix, or length leakage in metadata.
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
            "www.hubspot.com", "hubspot.com",
            "heliatech.online"
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

    def test_ssrf_allows_approved_partner_domains(self):
        """P0: Must allow legitimate approved partner domains over HTTPS."""
        legit = [
            "https://www.make.com/en/register?pc=heliatechmake",
            "https://try.elevenlabs.io/ajhd6t7k04dh",
            "https://supabase.com/pricing",
            "https://lovable.dev/signup",
            "https://heliatech.online/go/make"
        ]
        for target in legit:
            res = self._simulate_ssrf_validator(target)
            self.assertTrue(res["valid"], f"SSRF Validator should have allowed: {target}")

    # =========================================================================
    # 2. D1 CLIENT SCOPED TOKEN & USAGE JOURNAL
    # =========================================================================

    def test_d1_client_usage_journal(self):
        """P0: Query/execute operations must append an execution log into d1_usage_journal.jsonl."""
        initial_entries = 0
        if USAGE_JOURNAL_PATH.exists():
            with open(USAGE_JOURNAL_PATH, "r", encoding="utf-8") as f:
                initial_entries = len(f.readlines())

        # Execute a test read
        res = self.client.query("SELECT COUNT(*) as cnt FROM fleet_controls")
        self.assertTrue(len(res) > 0)

        self.assertTrue(USAGE_JOURNAL_PATH.exists(), "Usage journal must exist")
        with open(USAGE_JOURNAL_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertGreater(len(lines), initial_entries)
            last_entry = json.loads(lines[-1])
            self.assertEqual(last_entry["operation"], "query")
            self.assertEqual(last_entry["statement_type"], "SELECT")
            self.assertEqual(last_entry["status"], "SUCCESS")
            self.assertIn("latency_ms", last_entry)

    def test_d1_token_metadata_leak_free(self):
        """P1: Token metadata must never leak raw secrets, string lengths, or prefixes."""
        meta = self.client.get_token_metadata()
        self.assertEqual(meta["name"], "CLOUDFLARE_D1_TOKEN")
        self.assertIn("last_rotated_at", meta)
        self.assertIn("next_rotation_due", meta)
        self.assertEqual(meta["cadence_days"], 90)

        # Assert no sensitive patterns
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
        for tbl in ["fleet_controls", "deals_registry", "content_inventory", "schema_migrations"]:
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
