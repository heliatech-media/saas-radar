#!/usr/bin/env python3
"""
HeliaTech Email Dispatch Utility
Sends transactional, outreach, and newsletter emails via Resend API
using the official verified domain address: partnership@heliatech.online.
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
DEFAULT_SENDER = "HeliaTech <partnership@heliatech.online>"

def send_email(to_email: str, subject: str, html_content: str, sender: str = DEFAULT_SENDER):
    if not RESEND_API_KEY:
        print("[ERROR] RESEND_API_KEY is not defined in .env or environment")
        return False

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "HeliaTech-Dispatcher/1.0"
    }

    payload = {
        "from": sender,
        "to": [to_email] if isinstance(to_email, str) else to_email,
        "subject": subject,
        "html": html_content
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[SUCCESS] Email dispatched to {to_email} (ID: {data.get('id')})")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[HTTP ERROR] Code {e.code}: {error_body}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Send an email from partnership@heliatech.online")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--html", required=True, help="HTML body or text message")
    parser.add_argument("--sender", default=DEFAULT_SENDER, help="Custom sender (default: HeliaTech <partnership@heliatech.online>)")
    args = parser.parse_args()

    success = send_email(args.to, args.subject, args.html, args.sender)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
