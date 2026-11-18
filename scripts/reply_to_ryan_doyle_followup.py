#!/usr/bin/env python3
"""
Follow-up reply to Ryan Doyle (Book a Sponsor) with HeliaTech's official Media Kit.
Sent from partnership@heliatech.online via Resend API.
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
SUBJECT = "Re: Outreach preview for HeliaTech Radar"

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #1e293b;">
<p>Hey Ryan,</p>

<p>Thanks for sharing the preview. The brand targets (MongoDB, Sentry, Tiger Data) are a great match for our software architecture and developer audience.</p>

<p>Here is our official media kit and sponsorship overview to include in your pitches:<br>
👉 <a href="https://heliatech.online/sponsor/" style="color: #0284c7; text-decoration: none; font-weight: 600;">https://heliatech.online/sponsor/</a></p>

<p>Key highlights for prospective sponsors:
<ul>
  <li><strong>Audience:</strong> Technical founders, CTOs, and software decision-makers (80%+ US &amp; Tier-1 traffic).</li>
  <li><strong>Newsletter Spotlight (The Thursday Radar):</strong> $250 / dispatch (exclusive solo sponsor slot, 45%+ executive open rate).</li>
  <li><strong>Featured Duel &amp; Directory Placement:</strong> $500 / month.</li>
  <li><strong>Dedicated Architectural Teardown:</strong> $1,200 / deep dive.</li>
</ul>
</p>

<p>We are set up to handle sponsor payments directly via wire transfer, ACH, corporate invoice, and PayPal.</p>

<p>Please feel free to loop us in as soon as positive responses come in.</p>

<p>Best regards,<br>
<strong>HeliaTech Partnerships Team</strong><br>
<a href="https://heliatech.online" style="color: #0284c7; text-decoration: none;">https://heliatech.online</a></p>
</body>
</html>
"""

PLAIN_TEXT = """Hey Ryan,

Thanks for sharing the preview. The brand targets (MongoDB, Sentry, Tiger Data) are a great match for our software architecture and developer audience.

Here is our official media kit and sponsorship overview to include in your pitches:
https://heliatech.online/sponsor/

Key highlights for prospective sponsors:
- Audience: Technical founders, CTOs, and software decision-makers (80%+ US & Tier-1 traffic).
- Newsletter Spotlight (The Thursday Radar): $250 / dispatch (exclusive solo sponsor slot, 45%+ executive open rate).
- Featured Duel & Directory Placement: $500 / month.
- Dedicated Architectural Teardown: $1,200 / deep dive.

We are set up to handle sponsor payments directly via wire transfer, ACH, corporate invoice, and PayPal.

Please feel free to loop us in as soon as positive responses come in.

Best regards,
HeliaTech Partnerships Team
https://heliatech.online
"""

def send():
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "HeliaTech-Partnerships/1.0"
    }
    
    payload = {
        "from": FROM_SENDER,
        "to": [TO_EMAIL],
        "reply_to": REPLY_TO,
        "subject": SUBJECT,
        "html": HTML_CONTENT,
        "text": PLAIN_TEXT,
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            res = json.loads(body)
            email_id = res.get("id", "UNKNOWN")
            print(f"[SUCCESS] Follow-up sent to {TO_EMAIL} (Resend ID: {email_id})")
            
            # Log in email ledger
            ledger_file = "reports/email_campaign_ledger.json"
            ledger = []
            if os.path.exists(ledger_file):
                try:
                    with open(ledger_file, "r", encoding="utf-8") as f:
                        ledger = json.load(f)
                except Exception:
                    ledger = []
            
            entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "action": "OUTBOUND_REPLY_FOLLOWUP_MEDIA_KIT",
                "recipient": TO_EMAIL,
                "sender": FROM_SENDER,
                "subject": SUBJECT,
                "resend_id": email_id,
                "status": "SENT"
            }
            ledger.append(entry)
            
            os.makedirs(os.path.dirname(ledger_file), exist_ok=True)
            with open(ledger_file, "w", encoding="utf-8") as f:
                json.dump(ledger, f, indent=2)
                
            return email_id
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        print(f"[ERROR] HTTP {e.code}: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    send()
