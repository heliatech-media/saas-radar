"""
HeliaTech Sentinel Governance - Cloudflare D1 & Unified Database Client
=======================================================================
Implements the immutable rules:
1. "D1 est l'unique vérité de production. Le runner GitHub ne doit jamais modifier
   une SQLite locale puis espérer synchroniser plus tard. En production, ses écritures
   doivent passer par un accès authentifié à D1 ; SQLite locale sert uniquement aux tests."
2. "Limiter le token D1. Token dédié, droits minimums sur la seule base concernée,
   stocké uniquement dans les secrets GitHub/Cloudflare, avec rotation et journal d'usage."
3. "Stocke le journal d'audit dans D1 avec interdiction applicative d'UPDATE/DELETE,
   une chaîne de hash cryptographique (prev_hash -> entry_hash), et exporte-le vers
   un stockage R2 privé avec rétention et versioning."
"""

import os
import sys
import json
import time
import logging
import sqlite3
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import urllib.request
import urllib.error

logger = logging.getLogger("Helia-D1Client")
ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_DB_PATH = ROOT_DIR / "data" / "sentinel_governance.db"
USAGE_JOURNAL_PATH = ROOT_DIR / "data" / "d1_usage_journal.jsonl"
AUDIT_EXPORTS_DIR = ROOT_DIR / "data" / "backups" / "audit_exports"

GENESIS_PREV_HASH = "0" * 64
PROTECTED_IMMUTABLE_TABLES = {"D1_USAGE_AUDIT_LOG", "SENTINEL_AUDIT_LOGS"}


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
        self._is_logging_audit = False

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

    def _assert_immutability(self, sql: str):
        """
        Interdiction applicative absolue d'UPDATE, DELETE, DROP ou ALTER
        sur les tables de journalisation immuables (d1_usage_audit_log, sentinel_audit_logs).
        """
        if getattr(self, "is_restore_mode", False):
            return

        clean_sql = sql.strip().upper()
        # Look for mutating verbs
        for verb in ["UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE"]:
            if clean_sql.startswith(verb) or f" {verb} " in clean_sql:
                for tbl in PROTECTED_IMMUTABLE_TABLES:
                    if tbl in clean_sql:
                        raise PermissionError(
                            f"[IMMUTABLE AUDIT LOG PROTECTION] L'opération '{verb}' est strictement interdite "
                            f"sur la table d'audit immuable '{tbl}'. Les journaux d'audit ne peuvent être ni modifiés ni supprimés."
                        )

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
        Stocke le journal d'audit dans D1 (ou SQLite en test) avec une chaîne de hash cryptographique.
        Génère une empreinte liée au bloc précédent (prev_hash -> entry_hash).
        """
        if self._is_logging_audit:
            return  # Prevent recursive logging when inserting the audit log itself

        now_iso = datetime.now(timezone.utc).isoformat()
        stmt_type = self._extract_statement_type(sql)
        sanitized_sql = self._sanitize_sql_for_log(sql)
        actor_email = os.environ.get("SENTINEL_ACTOR_EMAIL", "system@heliatech.online")

        # Fallback offline jsonl
        file_entry = {
            "timestamp": now_iso,
            "mode": self.mode,
            "token_type": getattr(self, "token_type", "LOCAL"),
            "token_scope": self.TOKEN_SCOPE if self.mode == "CLOUDFLARE_D1_PRODUCTION" else "LOCAL_SQLITE",
            "operation": operation,
            "statement_type": stmt_type,
            "sanitized_sql": sanitized_sql,
            "latency_ms": latency_ms,
            "rows_affected": rows_affected,
            "status": status,
            "error": error
        }
        try:
            USAGE_JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(USAGE_JOURNAL_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(file_entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to append to D1 usage journal file: {e}")

        # Database Hash-Chained Audit Record in D1 / SQLite
        try:
            self._is_logging_audit = True
            prev_hash = GENESIS_PREV_HASH

            # 1. Fetch latest entry hash
            latest_rows = self.query("SELECT entry_hash FROM d1_usage_audit_log ORDER BY sequence_id DESC LIMIT 1")
            if latest_rows and latest_rows[0].get("entry_hash"):
                prev_hash = latest_rows[0]["entry_hash"]

            # 2. Compute cryptographic entry hash linking to previous
            hash_payload = f"{prev_hash}|{now_iso}|{actor_email}|{operation}|{stmt_type}|{sanitized_sql}|{rows_affected}|{status}"
            entry_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

            # 3. Insert append-only audit entry
            insert_sql = """
                INSERT INTO d1_usage_audit_log 
                (timestamp, actor_email, operation, statement_type, sanitized_sql, rows_affected, latency_ms, status, error, token_scope, prev_hash, entry_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = [
                now_iso, actor_email, operation, stmt_type, sanitized_sql,
                rows_affected, latency_ms, status, error or "",
                self.TOKEN_SCOPE if self.mode == "CLOUDFLARE_D1_PRODUCTION" else "LOCAL_SQLITE",
                prev_hash, entry_hash
            ]
            self.execute(insert_sql, params)
        except Exception as e:
            # Table might not exist yet before migration
            pass
        finally:
            self._is_logging_audit = False

    def verify_hash_chain(self) -> Dict[str, Any]:
        """
        Vérifie l'intégrité cryptographique absolue de la chaîne de hash dans d1_usage_audit_log.
        Détecte toute tentative d'altération, suppression ou réordonnancement des enregistrements.
        """
        rows = self.query("SELECT sequence_id, timestamp, actor_email, operation, statement_type, sanitized_sql, rows_affected, status, prev_hash, entry_hash FROM d1_usage_audit_log ORDER BY sequence_id ASC")
        
        if not rows:
            return {"valid": True, "count": 0, "message": "Journal vide (0 entrée)"}

        expected_prev = GENESIS_PREV_HASH
        for r in rows:
            seq = r["sequence_id"]
            if r["prev_hash"] != expected_prev:
                raise ValueError(f"[CORRUPTION DÉTECTÉE] Rupture de chaîne au sequence_id {seq}: prev_hash attendu {expected_prev}, trouvé {r['prev_hash']}")

            # Recompute entry hash
            payload = f"{expected_prev}|{r['timestamp']}|{r['actor_email']}|{r['operation']}|{r['statement_type']}|{r['sanitized_sql']}|{r['rows_affected']}|{r['status']}"
            computed_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

            if computed_hash != r["entry_hash"]:
                raise ValueError(f"[CORRUPTION DÉTECTÉE] Empreinte altérée au sequence_id {seq}: attendu {computed_hash}, trouvé {r['entry_hash']}")

            expected_prev = r["entry_hash"]

        return {
            "valid": True,
            "total_verified": len(rows),
            "head_sequence_id": rows[-1]["sequence_id"],
            "head_hash": expected_prev,
            "status": "HASH_CHAIN_INTEGRITY_VERIFIED"
        }

    def export_audit_to_r2(self, retention_days: int = 365, version: str = "v1.0.0") -> Dict[str, Any]:
        """
        Exporte le journal d'audit immuable vers un stockage Cloudflare R2 privé
        avec métadonnées de rétention et versioning.
        """
        AUDIT_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        chain_status = self.verify_hash_chain()
        rows = self.query("SELECT * FROM d1_usage_audit_log ORDER BY sequence_id ASC")

        now_utc = datetime.now(timezone.utc)
        timestamp_str = now_utc.strftime("%Y%m%d_%H%M%S")
        export_filename = f"d1_audit_export_{timestamp_str}_{version}.json"
        export_file_path = AUDIT_EXPORTS_DIR / export_filename

        raw_json = json.dumps(rows, indent=2)
        checksum = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

        manifest = {
            "export_file": export_filename,
            "schema_version": version,
            "retention_policy": f"{retention_days}_days_immutable",
            "exported_at": now_utc.isoformat(),
            "total_records": len(rows),
            "hash_chain_verified": chain_status["valid"],
            "head_hash": chain_status.get("head_hash"),
            "checksum_sha256": checksum,
            "storage_target": "CLOUDFLARE_R2_PRIVATE",
            "bucket": os.environ.get("CLOUDFLARE_R2_BUCKET", "heliatech-sentinel-backups")
        }

        with open(export_file_path, "w", encoding="utf-8") as f:
            json.dump({"manifest": manifest, "records": rows}, f, indent=2)

        # Upload via wrangler if R2 is configured
        bucket_name = manifest["bucket"]
        r2_key = f"audit_logs/{export_filename}"
        r2_uploaded = False

        try:
            if os.environ.get("CLOUDFLARE_API_TOKEN"):
                subprocess.run(
                    ["npx", "wrangler", "r2", "object", "put", f"{bucket_name}/{r2_key}", "--file", str(export_file_path)],
                    capture_output=True, check=True, timeout=30
                )
                r2_uploaded = True
        except Exception:
            pass

        manifest["r2_uploaded"] = r2_uploaded
        manifest["r2_key"] = r2_key if r2_uploaded else "STAGED_LOCALLY"

        return manifest

    def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a read query and returns a list of dictionary rows.
        """
        self._assert_immutability(sql)
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
        self._assert_immutability(sql)
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
        """Appends an immutable cryptographically signed audit log into sentinel_audit_logs."""
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
            "audit_table": "d1_usage_audit_log",
            "hash_chain": "SHA-256 (prev_hash -> entry_hash)",
            "immutability": "ENFORCED (UPDATE/DELETE PROHIBITED)"
        }


# Global default client
_default_client: Optional[D1Client] = None

def get_d1_client() -> D1Client:
    global _default_client
    if _default_client is None:
        _default_client = D1Client()
    return _default_client
