#!/usr/bin/env python3
"""
HeliaTech Sentinel - Cloudflare D1 & SQLite Migration Manager
=============================================================
Separates migration pipelines for:
  - test:    isolated local SQLite database (for tests/CI)
  - preprod: staging D1 database
  - prod:    production Cloudflare D1 database (Single Source of Truth)

Tracks schema version, checksum, timestamp, and actor in `schema_migrations`.
"""

import os
import sys
import argparse
import hashlib
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT_DIR / "data" / "migrations"
LOCAL_TEST_DB = ROOT_DIR / "data" / "sentinel_governance.db"

sys.path.insert(0, str(ROOT_DIR))
from agents.d1_client import D1Client


def compute_checksum(filepath: Path) -> str:
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def get_client_for_env(env: str) -> D1Client:
    if env == "test":
        return D1Client(local_db_path=LOCAL_TEST_DB, force_local=True)
    elif env == "preprod":
        db_id = os.environ.get("CLOUDFLARE_D1_PREPROD_ID", os.environ.get("CLOUDFLARE_D1_DATABASE_ID"))
        return D1Client(database_id=db_id)
    elif env == "prod":
        return D1Client()
    else:
        raise ValueError(f"Unknown environment: {env}. Must be 'test', 'preprod', or 'prod'.")


def ensure_migrations_table(client: D1Client):
    sql = """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        environment TEXT NOT NULL,
        applied_at TEXT NOT NULL,
        checksum TEXT NOT NULL,
        applied_by TEXT NOT NULL
    );
    """
    client.execute(sql)


def get_applied_migrations(client: D1Client, env: str) -> dict:
    ensure_migrations_table(client)
    rows = client.query("SELECT version, name, applied_at, checksum FROM schema_migrations ORDER BY version ASC")
    return {r["version"]: r for r in rows}


def list_migration_files() -> list:
    if not MIGRATIONS_DIR.exists():
        return []
    files = sorted(list(MIGRATIONS_DIR.glob("*.sql")))
    parsed = []
    for f in files:
        prefix = f.name.split("_")[0]
        try:
            ver = int(prefix)
            parsed.append((ver, f))
        except ValueError:
            continue
    return sorted(parsed, key=lambda x: x[0])


def status(env: str):
    client = get_client_for_env(env)
    applied = get_applied_migrations(client, env)
    available = list_migration_files()

    print(f"\n=======================================================")
    print(f" HeliaTech Sentinel Migration Status [Environment: {env.upper()}]")
    print(f" Mode: {client.mode}")
    print(f"=======================================================")

    if not available:
        print("No migration files found in data/migrations/")
        return

    for ver, fpath in available:
        if ver in applied:
            rec = applied[ver]
            status_str = f"APPLIED at {rec['applied_at']}"
            print(f" [OK] v{ver:04d} - {fpath.name} ({status_str})")
        else:
            print(f" [  ] v{ver:04d} - {fpath.name} (PENDING)")
    print("=======================================================\n")


def migrate(env: str, actor: str = "owner"):
    client = get_client_for_env(env)
    ensure_migrations_table(client)
    applied = get_applied_migrations(client, env)
    available = list_migration_files()

    pending = [(ver, fpath) for ver, fpath in available if ver not in applied]
    if not pending:
        print(f"Environment '{env}' is already up-to-date with all migrations.")
        return

    print(f"Applying {len(pending)} pending migrations to '{env}' ({client.mode})...")

    for ver, fpath in pending:
        checksum = compute_checksum(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Split statements by semicolon
        statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]
        for stmt in statements:
            client.execute(stmt)

        now_iso = datetime.now(timezone.utc).isoformat()
        client.execute(
            """
            INSERT OR REPLACE INTO schema_migrations (version, name, environment, applied_at, checksum, applied_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [ver, fpath.name, env, now_iso, checksum, actor]
        )

        client.log_audit(
            actor_email=actor,
            action="SCHEMA_MIGRATION_APPLIED",
            target=f"migration:v{ver:04d}",
            details={"version": ver, "file": fpath.name, "checksum": checksum, "env": env},
            new_state=f"v{ver:04d}_APPLIED"
        )
        print(f"  [OK] Applied v{ver:04d}: {fpath.name} (Checksum: {checksum[:12]}...)")

    print(f"\nAll migrations successfully applied to '{env}'.\n")


def main():
    parser = argparse.ArgumentParser(description="HeliaTech Sentinel D1/SQLite Migration Manager")
    parser.add_argument("--env", choices=["test", "preprod", "prod"], default="test", help="Target environment")
    parser.add_argument("--status", action="store_true", help="Display migration status")
    parser.add_argument("--migrate", action="store_true", help="Apply pending migrations")
    parser.add_argument("--actor", default="owner@heliatech.online", help="Actor email executing migration")

    args = parser.parse_args()

    if args.status:
        status(args.env)
    elif args.migrate:
        migrate(args.env, args.actor)
    else:
        status(args.env)


if __name__ == "__main__":
    main()
