#!/usr/bin/env python3
"""
Reply to Ryan Doyle (Book a Sponsor) from partnership@heliatech.online
Removes personal names; signs exclusively as HeliaTech Partnerships Team.
"""

import os
import sys
import json
import datetime
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if not RESEND_API_KEY:
    print("[ERROR] RESEND_API_KEY is missing from .env")
    sys.exit(1)

TO_EMAIL = "doyle@emaildoyle.co"
FROM_SENDER = "HeliaTech Partnerships <partnership@heliatech.online>"
REPLY_TO = "partnership@heliatech.online"
SUBJECT = "Re: Hi HeliaTech Radar team"

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1e293b;">
<p>Hey Ryan,</p>

<p>Sounds interesting. Feel free to put together the custom sample for HeliaTech Radar and send over the link.</p>

<p>Looking forward to seeing what brands you've mapped out for our niche.</p>

<p>Best regards,<br>
<strong>HeliaTech Partnerships Team</strong><br>
<a href="https://heliatech.online" style="color: #0284c7; text-decoration: none;">https://heliatech.online</a></p>
</body>
</html>
"""

def send():
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "HeliaTech-Dispatcher/1.0"
    }

    payload = {
        "from": FROM_SENDER,
        "to": [TO_EMAIL],
        "reply_to": REPLY_TO,
        "subject": SUBJECT,
        "html": HTML_CONTENT
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            message_id = res_data.get("id")
            print(f"[SUCCESS] Email dispatched successfully to {TO_EMAIL} (Resend ID: {message_id})")

            # Log to email ledger
            ledger_path = "reports/email_campaign_ledger.json"
            if os.path.exists(ledger_path):
                try:
                    with open(ledger_path, "r", encoding="utf-8") as f:
                        ledger = json.load(f)
                    ledger["dispatches"].insert(0, {
                        "type": "sponsor_outreach_reply",
                        "recipient": TO_EMAIL,
                        "from": "partnership@heliatech.online",
                        "subject": SUBJECT,
                        "dispatched_at": datetime.datetime.utcnow().isoformat() + "Z",
                        "resend_id": message_id
                    })
                    ledger["total_sent"] = ledger.get("total_sent", 0) + 1
                    with open(ledger_path, "w", encoding="utf-8") as f:
                        json.dump(ledger, f, indent=2)
                    print("[INFO] Ledger updated.")
                except Exception as ex:
                    print(f"[WARN] Failed to update ledger: {ex}")

            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[HTTP ERROR] Code {e.code}: {error_body}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    success = send()
    sys.exit(0 if success else 1)
