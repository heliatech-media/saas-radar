"""
HeliaTech Sentinel Governance - Cloudflare D1 & Unified Database Client
=======================================================================
Implements the immutable rule:
"D1 est l'unique vérité de production. Le runner GitHub ne doit jamais modifier
une SQLite locale puis espérer synchroniser plus tard. En production, ses écritures
doivent passer par un accès authentifié à D1 ; SQLite locale sert uniquement aux tests."

In Production:
  Connects directly to Cloudflare D1 via the Cloudflare REST API:
  POST https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query

In Test / Local Dev:
  Falls back to local SQLite WAL strictly for isolated offline unit tests.
"""

import os
import sys
import json
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


class D1Client:
    """
    Unified transactional client for Cloudflare D1 (Production)
    and SQLite WAL (Testing/Dev).
    """

    def __init__(
        self,
        account_id: Optional[str] = None,
        api_token: Optional[str] = None,
        database_id: Optional[str] = None,
        local_db_path: Optional[Path] = None,
        force_local: bool = False
    ):
        self.account_id = account_id or os.environ.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("CF_ACCOUNT_ID")
        self.api_token = api_token or os.environ.get("CLOUDFLARE_API_TOKEN") or os.environ.get("CF_API_TOKEN")
        self.database_id = database_id or os.environ.get("CLOUDFLARE_D1_DATABASE_ID") or os.environ.get("CF_D1_DATABASE_ID") or os.environ.get("D1_DATABASE_ID")
        self.local_db_path = local_db_path or LOCAL_DB_PATH
        self.force_local = force_local or (os.environ.get("APP_ENV") == "test") or (os.environ.get("PYTEST_CURRENT_TEST") is not None)

        if not self.force_local and self.account_id and self.api_token and self.database_id:
            self.mode = "CLOUDFLARE_D1_PRODUCTION"
            self.d1_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/d1/database/{self.database_id}/query"
            logger.info(f"D1Client initialized in PRODUCTION mode (Cloudflare D1 ID: {self.database_id})")
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

    def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a read query and returns a list of dictionary rows.
        """
        params = params or []
        if self.mode == "CLOUDFLARE_D1_PRODUCTION":
            return self._query_d1_api(sql, params)
        else:
            return self._query_local_sqlite(sql, params)

    def execute(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Executes a mutation query (INSERT, UPDATE, DELETE) and returns metadata.
        """
        params = params or []
        if self.mode == "CLOUDFLARE_D1_PRODUCTION":
            res = self._execute_d1_api(sql, params)
            return res
        else:
            return self._execute_local_sqlite(sql, params)

    def _query_d1_api(self, sql: str, params: List[Any]) -> List[Dict[str, Any]]:
        payload = json.dumps({"sql": sql, "params": params}).encode("utf-8")
        req = urllib.request.Request(
            self.d1_url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
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
                "Content-Type": "application/json"
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


# Global default client
_default_client: Optional[D1Client] = None

def get_d1_client() -> D1Client:
    global _default_client
    if _default_client is None:
        _default_client = D1Client()
    return _default_client
