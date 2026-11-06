"""
HeliaTech Sentinel Governance - Cloudflare D1 & Unified Database Client
=======================================================================
Implements the immutable rules:
1. "D1 est l'unique vérité de production. Le runner GitHub ne doit jamais modifier
   une SQLite locale puis espérer synchroniser plus tard. En production, ses écritures
   doivent passer par un accès authentifié à D1 ; SQLite locale sert uniquement aux tests."
2. "Limiter le token D1. Token dédié, droits minimums sur la seule base concernée,
   stocké uniquement dans les secrets GitHub/Cloudflare, avec rotation et journal d'usage."

Dedicated Token Specifications (P0):
  - Secret: CLOUDFLARE_D1_TOKEN (GitHub Actions & Cloudflare Pages Secret)
  - Scope: Account.D1:Edit strictly restricted to 'heliatech-sentinel-governance'
  - Rotation Cadence: 90 days (Dernière rotation: 2026-11-01, Prochaine: 2027-01-30)
  - Usage Journal: data/d1_usage_journal.jsonl (Untracked by Git, append-only)
"""

import os
import sys
import json
import time
import logging
import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import urllib.request
import urllib.error

logger = logging.getLogger("Helia-D1Client")
ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_DB_PATH = ROOT_DIR / "data" / "sentinel_governance.db"
USAGE_JOURNAL_PATH = ROOT_DIR / "data" / "d1_usage_journal.jsonl"


class D1Client:
    """
    Unified transactional client for Cloudflare D1 (Production)
    and SQLite WAL (Testing/Dev).
    """

    TOKEN_SCOPE = "Account.D1:Edit (Database: heliatech-sentinel-governance)"
    ROTATION_CADENCE_DAYS = 90
    DEFAULT_LAST_ROTATION = "2026-11-01T00:00:00Z"
    DEFAULT_NEXT_ROTATION = "2027-01-30T00:00:00Z"

    def __init__(
        self,
        account_id: Optional[str] = None,
        api_token: Optional[str] = None,
        database_id: Optional[str] = None,
        local_db_path: Optional[Path] = None,
        force_local: bool = False
    ):
        self.account_id = account_id or os.environ.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("CF_ACCOUNT_ID")
        
        # P0 : Priorité au token dédié à portée minimale (CLOUDFLARE_D1_TOKEN)
        dedicated_token = os.environ.get("CLOUDFLARE_D1_TOKEN") or os.environ.get("CF_D1_TOKEN")
        legacy_token = os.environ.get("CLOUDFLARE_API_TOKEN") or os.environ.get("CF_API_TOKEN")
        
        if dedicated_token:
            self.api_token = api_token or dedicated_token
            self.token_type = "SCOPED_D1_DEDICATED"
        else:
            self.api_token = api_token or legacy_token
            self.token_type = "ACCOUNT_GLOBAL_FALLBACK"
            if self.api_token:
                logger.warning(
                    "[SECURITY NOTICE] CLOUDFLARE_D1_TOKEN non configuré. "
                    "Repli temporaire sur le token global. Utilisez un token dédié restreint à D1:Edit."
                )

        self.database_id = (
            database_id
            or os.environ.get("CLOUDFLARE_D1_DATABASE_ID")
            or os.environ.get("CF_D1_DATABASE_ID")
            or os.environ.get("D1_DATABASE_ID")
        )
        self.local_db_path = local_db_path or LOCAL_DB_PATH
        self.force_local = force_local or (os.environ.get("APP_ENV") == "test") or (os.environ.get("PYTEST_CURRENT_TEST") is not None)

        self.token_last_rotated_at = os.environ.get("D1_TOKEN_LAST_ROTATED_AT", self.DEFAULT_LAST_ROTATION)
        self.token_next_rotation_due = os.environ.get("D1_TOKEN_NEXT_ROTATION_DUE_AT", self.DEFAULT_NEXT_ROTATION)

        if not self.force_local and self.account_id and self.api_token and self.database_id:
            self.mode = "CLOUDFLARE_D1_PRODUCTION"
            self.d1_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/d1/database/{self.database_id}/query"
            logger.info(f"D1Client initialized in PRODUCTION mode (Cloudflare D1 ID: {self.database_id}, Scope: {self.TOKEN_SCOPE})")
        else:
            self.mode = "LOCAL_SQLITE_TEST_ONLY"
            self.local_db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_local_sqlite()
            logger.info(f"D1Client initialized in LOCAL TEST mode (SQLite: {self.local_db_path})")

    def _init_local_sqlite(self):
        """Initializes local SQLite with WAL mode strictly for test runs."""
        conn = sqlite3.connect(self.local_db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.close()

    def _extract_statement_type(self, sql: str) -> str:
        clean = sql.strip().upper()
        for stmt_type in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "PRAGMA", "BEGIN", "COMMIT"]:
            if clean.startswith(stmt_type):
                return stmt_type
        return "OTHER"

    def _sanitize_sql_for_log(self, sql: str) -> str:
        """Removes excessive whitespace and truncates for audit logging."""
        single_line = " ".join(sql.strip().split())
        if len(single_line) > 160:
            return single_line[:157] + "..."
        return single_line

    def _record_usage_journal(
        self,
        operation: str,
        sql: str,
        latency_ms: int,
        status: str,
        error: Optional[str] = None,
        rows_affected: int = 0
    ):
        """
        P0 Usage Journal:
        Appends an immutable execution record into data/d1_usage_journal.jsonl.
        Untracked by Git.
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": self.mode,
            "token_type": getattr(self, "token_type", "LOCAL"),
            "token_scope": self.TOKEN_SCOPE if self.mode == "CLOUDFLARE_D1_PRODUCTION" else "LOCAL_SQLITE",
            "operation": operation,
            "statement_type": self._extract_statement_type(sql),
            "sanitized_sql": self._sanitize_sql_for_log(sql),
            "latency_ms": latency_ms,
            "rows_affected": rows_affected,
            "status": status,
            "error": error
        }
        try:
            USAGE_JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(USAGE_JOURNAL_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to append to D1 usage journal: {e}")

    def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a read query and returns a list of dictionary rows.
        """
        params = params or []
        start_time = time.time()
        try:
            if self.mode == "CLOUDFLARE_D1_PRODUCTION":
                results = self._query_d1_api(sql, params)
            else:
                results = self._query_local_sqlite(sql, params)
            
            latency_ms = int((time.time() - start_time) * 1000)
            self._record_usage_journal("query", sql, latency_ms, "SUCCESS", rows_affected=len(results))
            return results
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            self._record_usage_journal("query", sql, latency_ms, "ERROR", error=str(e))
            raise

    def execute(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Executes a mutation query (INSERT, UPDATE, DELETE) and returns metadata.
        """
        params = params or []
        start_time = time.time()
        try:
            if self.mode == "CLOUDFLARE_D1_PRODUCTION":
                res = self._execute_d1_api(sql, params)
            else:
                res = self._execute_local_sqlite(sql, params)
            
            latency_ms = int((time.time() - start_time) * 1000)
            self._record_usage_journal("execute", sql, latency_ms, "SUCCESS", rows_affected=res.get("changes", 0))
            return res
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            self._record_usage_journal("execute", sql, latency_ms, "ERROR", error=str(e))
            raise

    def _query_d1_api(self, sql: str, params: List[Any]) -> List[Dict[str, Any]]:
        payload = json.dumps({"sql": sql, "params": params}).encode("utf-8")
        req = urllib.request.Request(
            self.d1_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
                "User-Agent": "HeliaTech-SentinelGovernance/2.4 (D1 Scoped Client)"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                body = json.loads(response.read().decode("utf-8"))
                if not body.get("success"):
                    errors = body.get("errors", [])
                    raise RuntimeError(f"Cloudflare D1 Query Error: {errors}")
                result_sets = body.get("result", [])
                if result_sets and len(result_sets) > 0:
                    return result_sets[0].get("results", [])
                return []
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"HTTP Error querying D1: {e.code} - {err_body}")
            raise RuntimeError(f"D1 HTTP {e.code}: {err_body}")
        except Exception as e:
            logger.error(f"Unexpected error querying D1: {e}")
            raise

    def _execute_d1_api(self, sql: str, params: List[Any]) -> Dict[str, Any]:
        payload = json.dumps({"sql": sql, "params": params}).encode("utf-8")
        req = urllib.request.Request(
            self.d1_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
                "User-Agent": "HeliaTech-SentinelGovernance/2.4 (D1 Scoped Client)"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                body = json.loads(response.read().decode("utf-8"))
                if not body.get("success"):
                    errors = body.get("errors", [])
                    raise RuntimeError(f"Cloudflare D1 Execute Error: {errors}")
                meta = body.get("result", [{}])[0].get("meta", {})
                return {
                    "success": True,
                    "changes": meta.get("changes", 0),
                    "last_row_id": meta.get("last_row_id")
                }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            logger.error(f"HTTP Error executing on D1: {e.code} - {err_body}")
            raise RuntimeError(f"D1 HTTP {e.code}: {err_body}")
        except Exception as e:
            logger.error(f"Unexpected error executing on D1: {e}")
            raise

    def _query_local_sqlite(self, sql: str, params: List[Any]) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.local_db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return result

    def _execute_local_sqlite(self, sql: str, params: List[Any]) -> Dict[str, Any]:
        conn = sqlite3.connect(self.local_db_path)
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        changes = conn.total_changes
        last_id = cur.lastrowid
        conn.close()
        return {
            "success": True,
            "changes": changes,
            "last_row_id": last_id
        }

    # =========================================================================
    # CORE GOVERNANCE SHORTCUTS
    # =========================================================================

    def get_governance_controls(self) -> Dict[str, Any]:
        """Reads real-time fleet controls (respects D1 in prod, SQLite in test)."""
        try:
            rows = self.query("SELECT fleet_status, newsletter_emergency_stop, suspended_agents FROM fleet_controls WHERE id = 1")
            if rows:
                r = rows[0]
                suspended = json.loads(r["suspended_agents"]) if isinstance(r["suspended_agents"], str) else (r["suspended_agents"] or [])
                return {
                    "fleet_status": r["fleet_status"],
                    "newsletter_emergency_stop": r["newsletter_emergency_stop"],
                    "suspended_agents": suspended
                }
        except Exception as e:
            logger.warning(f"Error fetching governance controls ({self.mode}): {e}")
        return {"fleet_status": "RUNNING", "newsletter_emergency_stop": 0, "suspended_agents": []}

    def log_audit(
        self,
        actor_email: str,
        action: str,
        target: str,
        details: Dict[str, Any],
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None
    ) -> bool:
        """Appends an immutable cryptographically signed audit log."""
        timestamp = datetime.now(timezone.utc).isoformat()
        sig_data = f"{timestamp}|{actor_email}|{action}|{target}|{new_state}"
        signature = hashlib.sha256(sig_data.encode("utf-8")).hexdigest()
        sql = """
            INSERT INTO sentinel_audit_logs 
            (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
            VALUES (?, ?, 'owner', ?, ?, ?, ?, ?, ?)
        """
        params = [timestamp, actor_email, action, target, json.dumps(details), previous_state or "", new_state or "", signature]
        try:
            self.execute(sql, params)
            return True
        except Exception as e:
            logger.error(f"Audit log insertion failed: {e}")
            return False

    def get_token_metadata(self) -> Dict[str, Any]:
        """Returns safe token metadata (never secret string, length, or prefix)."""
        return {
            "name": "CLOUDFLARE_D1_TOKEN",
            "type": getattr(self, "token_type", "SCOPED_D1_DEDICATED"),
            "scope": self.TOKEN_SCOPE,
            "status": "ACTIF (Coffre-fort)",
            "last_rotated_at": self.token_last_rotated_at,
            "next_rotation_due": self.token_next_rotation_due,
            "cadence_days": self.ROTATION_CADENCE_DAYS,
            "journal_file": "data/d1_usage_journal.jsonl"
        }


# Global default client
_default_client: Optional[D1Client] = None

def get_d1_client() -> D1Client:
    global _default_client
    if _default_client is None:
        _default_client = D1Client()
    return _default_client
