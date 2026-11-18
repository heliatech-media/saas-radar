import sqlite3
import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

print("="*50)
print("1. LOCAL SQLITE DATABASES AUDIT")
print("="*50)

for db_path in ['data/newsletter_governance.db', 'data/sentinel_governance.db']:
    if not os.path.exists(db_path):
        print(f"File {db_path} does not exist.")
        continue
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        print(f"\n📂 Database: {db_path}")
        print(f"Tables: {tables}")
        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM `{t}`")
                cnt = cur.fetchone()[0]
                print(f"  • {t}: {cnt} rows")
                # Look for subscriber/email columns
                cur.execute(f"PRAGMA table_info(`{t}`)")
                cols = [c[1] for c in cur.fetchall()]
                if any(k in c.lower() for c in cols for k in ['email', 'subscriber']):
                    print(f"    -> Columns: {cols}")
                    cur.execute(f"SELECT * FROM `{t}` LIMIT 3")
                    sample = cur.fetchall()
                    print(f"    -> Sample rows: {sample}")
            except Exception as e:
                print(f"  • {t}: error reading count ({e})")
        conn.close()
    except Exception as e:
        print(f"Error checking {db_path}: {e}")

print("\n" + "="*50)
print("2. CLOUDFLARE D1 REMOTE DATABASE AUDIT")
print("="*50)

account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
database_id = os.getenv("CLOUDFLARE_D1_DATABASE_ID")
token = os.getenv("CLOUDFLARE_D1_TOKEN") or os.getenv("CLOUDFLARE_API_TOKEN")

if account_id and database_id and token:
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Query tables in D1
    queries = [
        "SELECT name FROM sqlite_master WHERE type='table';",
        "SELECT COUNT(*) AS total_subscribers FROM subscribers;",
        "SELECT COUNT(*) AS active_subscribers FROM subscribers WHERE status = 'active';",
        "SELECT email, status, created_at FROM subscribers ORDER BY created_at DESC LIMIT 5;"
    ]
    
    for q in queries:
        try:
            req = urllib.request.Request(url, data=json.dumps({"sql": q}).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if res.get('success'):
                    results = res.get('result', [{}])[0].get('results', [])
                    print(f"\n[D1 Query] {q}")
                    print(f"Result: {json.dumps(results, indent=2)}")
                else:
                    print(f"\n[D1 Query Failed] {q} -> {res.get('errors')}")
        except Exception as e:
            print(f"[D1 Query Error] {q} -> {e}")
else:
    print("Cloudflare D1 credentials missing from .env")
