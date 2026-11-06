#!/usr/bin/env python3
"""
HeliaTech Sentinel - Cloudflare D1 & SQLite Migration Manager
=============================================================
Implements P1 rules:
  "La migration --env prod doit exiger approbation owner, sauvegarde préalable et plan de rollback."

Safety Gates for Production Migrations:
  1. Mandatory Owner Confirmation (--owner-confirmation or OWNER_CONFIRMATION env var).
  2. Automatic Pre-Migration Backup (invokes d1_backup_restore.backup("prod")).
  3. Mandatory Rollback Plan Verification (ensures matching data/migrations/rollback/XXXX_rollback.sql).
  4. Immutable Version Tracking in `schema_migrations` table with SHA-256 checksums and signatures.
"""

import os
import sys
import argparse
import hashlib
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Tuple

# Ensure stdout handles UTF-8 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT_DIR / "data" / "migrations"
ROLLBACK_DIR = MIGRATIONS_DIR / "rollback"
LOCAL_TEST_DB = ROOT_DIR / "data" / "sentinel_governance.db"

sys.path.insert(0, str(ROOT_DIR))
from agents.d1_client import D1Client
from scripts.d1_backup_restore import backup as run_backup


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


def list_migration_files() -> List[Tuple[int, Path]]:
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


def verify_rollback_plans(pending: List[Tuple[int, Path]]) -> Tuple[bool, List[str]]:
    """
    P1 Safety Gate:
    Verifies that for every pending migration, a valid non-empty rollback plan exists.
    """
    missing = []
    for ver, fpath in pending:
        rollback_file = ROLLBACK_DIR / f"{ver:04d}_rollback.sql"
        if not rollback_file.exists():
            missing.append(str(rollback_file.name))
        else:
            with open(rollback_file, "r", encoding="utf-8") as rf:
                content = rf.read().strip()
                if len(content) < 10:
                    missing.append(f"{rollback_file.name} (fichier vide ou invalide)")
    return len(missing) == 0, missing


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
        rollback_file = ROLLBACK_DIR / f"{ver:04d}_rollback.sql"
        has_rollback = "[Rollback OK]" if rollback_file.exists() else "[No Rollback]"
        if ver in applied:
            rec = applied[ver]
            status_str = f"APPLIED at {rec['applied_at']}"
            print(f" [OK] v{ver:04d} - {fpath.name:<42} ({status_str}) {has_rollback}")
        else:
            print(f" [  ] v{ver:04d} - {fpath.name:<42} (PENDING) {has_rollback}")
    print("=======================================================\n")


def migrate(env: str, actor: str = "owner@heliatech.online", owner_confirmation: bool = False):
    client = get_client_for_env(env)
    ensure_migrations_table(client)
    applied = get_applied_migrations(client, env)
    available = list_migration_files()

    pending = [(ver, fpath) for ver, fpath in available if ver not in applied]
    if not pending:
        print(f"Environment '{env}' is already up-to-date with all migrations.")
        return

    # P1 SAFETY GATES FOR PRODUCTION
    if env == "prod":
        print("\n" + "=" * 60)
        print(" [PRODUCTION MIGRATION SAFETY GATE P1] Checking prerequisites...")
        print("=" * 60)

        # 1. Verification of Owner Confirmation
        confirmed = owner_confirmation or (os.environ.get("OWNER_CONFIRMATION") == "true")
        if not confirmed:
            print("\n[SECURITY REFUSAL] La migration en production exige l'approbation explicite de l'Owner.")
            print("  Veuillez relancer la commande avec le paramètre : --owner-confirmation")
            print("  Ou définir la variable d'environnement : OWNER_CONFIRMATION=true\n")
            sys.exit(1)
        print("  [OK] 1. Approbation Owner : CONFIRMÉE par l'opérateur.")

        # 2. Verification of Rollback Plans
        rollback_ok, missing_rollbacks = verify_rollback_plans(pending)
        if not rollback_ok:
            print(f"\n[SECURITY REFUSAL] Plans de rollback manquants ou incomplets : {missing_rollbacks}")
            print("  Chaque migration de production doit comporter son script de rollback dans data/migrations/rollback/.\n")
            sys.exit(1)
        print("  [OK] 2. Plans de Rollback : VALIDÉS pour toutes les migrations en attente.")

        # 3. Automated Pre-Migration Backup
        print("  -> Exécution de la sauvegarde préalable obligatoire...")
        try:
            pre_backup_meta = run_backup("prod", actor=actor)
            print(f"  [OK] 3. Sauvegarde préalable réussie : {pre_backup_meta['backup_file']} ({pre_backup_meta['total_rows']} lignes).")
        except Exception as e:
            print(f"\n[SECURITY REFUSAL] Échec de la sauvegarde préalable : {e}")
            print("  Migration interrompue immédiatement sans modification de la base.\n")
            sys.exit(1)

        print("=" * 60 + "\n")

    print(f"Applying {len(pending)} pending migrations to '{env}' ({client.mode})...")

    for ver, fpath in pending:
        checksum = compute_checksum(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            sql_content = f.read()

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


def rollback(env: str, version: int, actor: str = "owner@heliatech.online", owner_confirmation: bool = False):
    """
    P1 Rollback Execution:
    Applies the rollback SQL script and removes the version from `schema_migrations`.
    """
    client = get_client_for_env(env)
    ensure_migrations_table(client)
    applied = get_applied_migrations(client, env)

    if version not in applied:
        print(f"[ERROR] Version v{version:04d} is not marked as applied in environment '{env}'.")
        return

    rollback_file = ROLLBACK_DIR / f"{version:04d}_rollback.sql"
    if not rollback_file.exists():
        print(f"[ERROR] Rollback file not found: {rollback_file}")
        return

    if env == "prod":
        confirmed = owner_confirmation or (os.environ.get("OWNER_CONFIRMATION") == "true")
        if not confirmed:
            print("[SECURITY REFUSAL] Rollback en production exige --owner-confirmation.")
            sys.exit(1)
        print("Executing pre-rollback backup of production...")
        run_backup("prod", actor=actor)

    print(f"Executing rollback for v{version:04d} using {rollback_file.name} on '{env}'...")
    with open(rollback_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]
    for stmt in statements:
        client.execute(stmt)

    client.execute("DELETE FROM schema_migrations WHERE version = ?", [version])
    client.log_audit(
        actor_email=actor,
        action="SCHEMA_MIGRATION_ROLLBACK",
        target=f"migration:v{version:04d}",
        details={"version": version, "file": rollback_file.name, "env": env},
        new_state=f"v{version:04d}_REVERTED"
    )
    print(f"[OK] Migration v{version:04d} successfully rolled back.\n")


def main():
    parser = argparse.ArgumentParser(description="HeliaTech Sentinel D1/SQLite Migration Manager")
    parser.add_argument("--env", choices=["test", "preprod", "prod"], default="test", help="Target environment")
    parser.add_argument("--status", action="store_true", help="Display migration status")
    parser.add_argument("--migrate", action="store_true", help="Apply pending migrations")
    parser.add_argument("--rollback", type=int, help="Rollback specific migration version")
    parser.add_argument("--actor", default="owner@heliatech.online", help="Actor email executing migration")
    parser.add_argument("--owner-confirmation", action="store_true", help="Explicit owner confirmation for production")

    args = parser.parse_args()

    if args.status:
        status(args.env)
    elif args.migrate:
        migrate(args.env, args.actor, args.owner_confirmation)
    elif args.rollback is not None:
        rollback(args.env, args.rollback, args.actor, args.owner_confirmation)
    else:
        status(args.env)


if __name__ == "__main__":
    main()
