#!/usr/bin/env python3
"""
HeliaTech Single Test Dispatcher - Issue #055
Sends a live rendered test email of Issue #055 to Hamza (hamzaelfahsi@gmail.com)
from radar@heliatech.online via Resend API.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.error
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER = "The Thursday Radar <radar@heliatech.online>"
TARGET_EMAIL = "hamzaelfahsi@gmail.com"
SUBJECT = "The State of AI-Assisted IDEs: Context Indexing and Multi-File Workflows"

def main():
    if not RESEND_API_KEY:
        print("[ERROR] RESEND_API_KEY not found in environment.")
        sys.exit(1)

    template_path = ROOT_DIR / "templates" / "emails" / "weekly_confidential.html"
    if not template_path.exists():
        print(f"[ERROR] Template {template_path} does not exist.")
        sys.exit(1)

    template_html = template_path.read_text(encoding="utf-8")

    context = {
        "issue_number": "055",
        "publish_date": "Thursday, Nov 19, 2026",
        "preheader_text": "Empirical benchmark on 450+ refactorings, Postiz 41k★ architecture teardown, and setup notes.",
        "issue_title": "The Autonomous IDE Shift: Why High-Velocity Teams Are Leaving Copilot for Cursor",
        "issue_headline": "The Autonomous IDE Shift: Why High-Velocity Teams Are Leaving Copilot for Cursor",
        "executive_summary": "We analyzed 450+ multi-file refactoring workflows across engineering teams. Here is how Cursor's context indexer cuts PR review cycles by 40%.",
        "teardown_tool_name": "Cursor",
        "teardown_tool_verdict_title": "Context-Engineered Development & The End of Shallow Autocomplete",
        "teardown_summary": "Standard inline autocompletion is obsolete. Cursor's deep multi-file repository graph indexing allows developers to write production full-stack code in minutes with zero context fragmentation.",
        "score_roi": "98%",
        "score_friction": "Low (9.5/10)",
        "score_overall": "9.9 / 10",
        "teardown_review_url": "https://heliatech.online/reviews/cursor/",
        "github_repo_name": "postiz-app / postiz",
        "github_stars": "41,883+",
        "github_stack": "Next.js 15, PostgreSQL, Redis BullMQ, Docker",
        "github_license": "AGPL-3.0",
        "github_summary": "Open-source social media management architecture with native Next.js 15, PostgreSQL, and BullMQ Redis queues.",
        "github_verdict": "Self-hosting saves $350/mo for marketing agencies. Clean Docker architecture with zero telemetry leaks.",
        "github_audit_url": "https://heliatech.online/repos/postiz/",
        "duel_title": "Cursor vs GitHub Copilot (2026 Developer Velocity Showdown)",
        "duel_takeaway": "Copilot struggles with multi-file architectures and hallucinated imports, while Cursor edits 10+ files simultaneously with strict TypeScript adherence.",
        "duel_winner_reason": "Cursor wins decisively with 3.2x faster task resolution and native .cursorrules enforcement.",
        "duel_url": "https://heliatech.online/versus/cursor-vs-github-copilot/",
        "deal_headline": "Cursor Rules Masterpack: Next.js 15, Tailwind & Supabase ($19)",
        "deal_description": "Download the audited blueprint ruleset used by leading agencies to eliminate 90% of boilerplate errors.",
        "deal_hop_link": "https://heliatech.online/templates/cursor-rules-nextjs-tailwind-supabase-masterpack/",
        "email": TARGET_EMAIL,
        "unsubscribe_url": f"https://heliatech.online/unsubscribe?email={TARGET_EMAIL}"
    }

    # Render template
    rendered_html = template_html
    for key, val in context.items():
        rendered_html = rendered_html.replace("{{" + key + "}}", str(val))

    # Send via Resend
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "HeliaTech-Dispatcher/1.0"
    }
    payload = {
        "from": SENDER,
        "to": [TARGET_EMAIL],
        "subject": SUBJECT,
        "html": rendered_html
    }

    print(f"[*] Dispatching test email to {TARGET_EMAIL} from {SENDER}...")
    print(f"[*] Subject: {SUBJECT}")

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            email_id = data.get("id")
            print(f"[SUCCESS] Test email successfully delivered via Resend!")
            print(f"[RESEND ID] {email_id}")
            print(f"[TIMESTAMP] {datetime.now().isoformat()}")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[HTTP ERROR] Code {e.code}: {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
