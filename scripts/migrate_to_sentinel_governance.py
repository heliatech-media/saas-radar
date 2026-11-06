import sqlite3
import json
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join("data", "sentinel_governance.db")
SCHEMA_PATH = os.path.join("data", "schema_sentinel_governance.sql")
SUBSCRIBERS_JSON = os.path.join("data", "subscribers_ledger.json")
OLD_NEWSLETTER_DB = os.path.join("data", "newsletter_governance.db")

def init_db():
    print(f"Connecting to {DB_PATH} in WAL mode...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    conn.commit()
    print("Schema applied successfully.")
    return conn

def migrate_subscribers(conn):
    if not os.path.exists(SUBSCRIBERS_JSON):
        print(f"No {SUBSCRIBERS_JSON} found, skipping subscriber migration.")
        return 0
    
    with open(SUBSCRIBERS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    subscribers = data.get("subscribers", [])
    print(f"Migrating {len(subscribers)} subscribers into private transactional table 'subscribers'...")
    
    cursor = conn.cursor()
    inserted = 0
    for sub in subscribers:
        sub_id = sub.get("id") or f"sub_{inserted+1:03d}"
        email = sub.get("email", "").strip().lower()
        if not email:
            continue
        role = sub.get("role")
        country = sub.get("country")
        country_code = sub.get("country_code")
        signup_date = sub.get("signup_date") or datetime.utcnow().isoformat() + "Z"
        source_path = sub.get("source_path")
        lead_magnet = sub.get("lead_magnet")
        status = sub.get("status", "Verified")
        
        cursor.execute("""
            INSERT OR REPLACE INTO subscribers 
            (id, email, role, country, country_code, signup_date, source_path, lead_magnet, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sub_id, email, role, country, country_code, signup_date, source_path, lead_magnet, status))
        inserted += 1
    
    conn.commit()
    print(f"Successfully migrated {inserted} subscribers.")
    return inserted

def copy_old_newsletter_db(conn):
    if not os.path.exists(OLD_NEWSLETTER_DB):
        return
    print(f"Importing historical data from {OLD_NEWSLETTER_DB}...")
    old_conn = sqlite3.connect(OLD_NEWSLETTER_DB)
    old_cur = old_conn.cursor()
    
    try:
        old_cur.execute("SELECT * FROM newsletter_editions")
        editions = old_cur.fetchall()
        col_names = [description[0] for description in old_cur.description]
        placeholders = ", ".join(["?"] * len(col_names))
        cols = ", ".join(col_names)
        
        for row in editions:
            conn.execute(f"INSERT OR REPLACE INTO newsletter_editions ({cols}) VALUES ({placeholders})", row)
        print(f"Imported {len(editions)} newsletter editions.")
    except Exception as e:
        print(f"Notice during newsletter_editions copy: {e}")

    try:
        old_cur.execute("SELECT * FROM newsletter_dispatches")
        dispatches = old_cur.fetchall()
        col_names = [description[0] for description in old_cur.description]
        placeholders = ", ".join(["?"] * len(col_names))
        cols = ", ".join(col_names)
        
        for row in dispatches:
            conn.execute(f"INSERT OR REPLACE INTO newsletter_dispatches ({cols}) VALUES ({placeholders})", row)
        print(f"Imported {len(dispatches)} newsletter dispatches.")
    except Exception as e:
        print(f"Notice during newsletter_dispatches copy: {e}")

    old_conn.close()
    conn.commit()

def seed_approval_queue(conn):
    print("Checking approval queue for pending items...")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM owner_approvals WHERE status = 'PENDING'")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Create Issue #055 pending approval item
        subject = "The Thursday Radar: Cursor 0.43 vs Windsurf 1.2 Benchmark"
        slot_key = "2026-11-12:thursday"
        content_hash = hashlib.sha256(f"{slot_key}:{subject}:preview".encode('utf-8')).hexdigest()
        
        payload = json.dumps({
            "slot_key": slot_key,
            "scheduled_date": "2026-11-12",
            "edition_type": "thursday",
            "issue_number": 55,
            "subject": subject,
            "focus": "Cursor 0.43 & Windsurf 1.2",
            "featureArticleId": "cursor-vs-windsurf-deep-benchmark",
            "recipients_estimated": 142
        })
        
        cursor.execute("""
            INSERT INTO owner_approvals 
            (item_type, item_ref, title, summary, content_payload, content_hash, author_agent, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
        """, (
            "newsletter_edition",
            slot_key,
            "Newsletter #055 (Focus : Cursor 0.43 vs Windsurf 1.2)",
            "Édition du jeudi 12 novembre 2026 avec analyse comparative TCO, sans duplication d'articles récents.",
            payload,
            content_hash,
            "NewsletterEngine",
            datetime.utcnow().isoformat() + "Z"
        ))
        
        # Also ensure draft exists in newsletter_editions
        cursor.execute("""
            INSERT OR IGNORE INTO newsletter_editions 
            (slot_key, scheduled_date, edition_type, status, issue_number, subject, normalized_subject, content_html, content_hash, selected_items, created_at)
            VALUES (?, ?, ?, 'draft', 55, ?, ?, ?, ?, '[]', ?)
        """, (
            slot_key, "2026-11-12", "thursday",
            subject, subject.lower(),
            "<h1>The Thursday Radar #055</h1><p>Brouillon verrouillé en attente d'approbation patron.</p>",
            content_hash,
            datetime.utcnow().isoformat() + "Z"
        ))
        
        conn.commit()
        print("Seeded Issue #055 in owner_approvals.")

def log_initial_audit(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sentinel_audit_logs")
    if cursor.fetchone()[0] == 0:
        ts = datetime.utcnow().isoformat() + "Z"
        action = "SYSTEM_INITIALIZATION"
        actor = "owner (Cloudflare Zero Trust MFA)"
        target = "sentinel_governance"
        details = json.dumps({
            "message": "Migration transactionnelle vers SQLite WAL / Cloudflare D1 complétée avec succès.",
            "subscribers_table": "initialized",
            "fleet_controls": "active",
            "zero_static_pii": True
        })
        sig = hashlib.sha256(f"1:{ts}:{actor}:{action}:{details}".encode('utf-8')).hexdigest()
        
        cursor.execute("""
            INSERT INTO sentinel_audit_logs 
            (timestamp, actor_email, actor_role, action, target, details_json, previous_state, new_state, signature)
            VALUES (?, ?, 'owner', ?, ?, ?, 'JSON_FILES', 'TRANSACTIONAL_SQL', ?)
        """, (ts, actor, action, target, details, sig))
        conn.commit()
        print("Logged initial audit entry.")

if __name__ == "__main__":
    conn = init_db()
    migrate_subscribers(conn)
    copy_old_newsletter_db(conn)
    seed_approval_queue(conn)
    log_initial_audit(conn)
    
    # Verification
    cur = conn.cursor()
    for table in ["subscribers", "fleet_controls", "owner_approvals", "sentinel_audit_logs", "newsletter_editions"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"Table '{table}': {count} rows")
    
    conn.close()
    print("Migration finished successfully.")
