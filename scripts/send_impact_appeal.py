#!/usr/bin/env python3
"""
HeliaTech Media - Official Impact.com Publisher Appeal Dispatcher
Sends the official manual reconsideration request directly from partnership@heliatech.online via Resend API.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if not RESEND_API_KEY:
    print("[ERROR] RESEND_API_KEY missing from environment / .env")
    sys.exit(1)

ACCOUNT_ID = "8110674"
SENDER = "HeliaTech Partnerships <partnership@heliatech.online>"
TO_RECIPIENTS = ["support@impact.com", "publisher-support@impact.com"]
CC_RECIPIENTS = ["hamzaelfahsi@gmail.com"]

SUBJECT = f"Appeal & Manual Review Request: Media Partner Account ID {ACCOUNT_ID} (HeliaTech Media)"

HTML_BODY = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8fafc; }}
  .container {{ max-width: 640px; margin: 0 auto; background: #ffffff; padding: 32px; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }}
  .header {{ border-bottom: 2px solid #0284c7; padding-bottom: 16px; margin-bottom: 24px; }}
  .badge {{ display: inline-block; padding: 4px 12px; background: #e0f2fe; color: #0369a1; border-radius: 9999px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }}
  .meta-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 24px 0; }}
  .meta-box ul {{ margin: 0; padding-left: 20px; }}
  .meta-box li {{ margin-bottom: 8px; }}
  .highlight {{ color: #0284c7; font-weight: 600; text-decoration: none; }}
  .footer {{ margin-top: 32px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 13px; color: #64748b; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <span class="badge">Official Publisher Appeal â€¢ Account ID {ACCOUNT_ID}</span>
    <h2 style="margin: 10px 0 0 0; color: #0f172a; font-size: 20px;">Manual Reconsideration Request: HeliaTech Media</h2>
  </div>

  <p>Dear Impact.com Publisher Onboarding & Review Team,</p>

  <p>I am writing to formally request a manual human review of our media partner application for <strong>HeliaTech Media</strong> under <strong>Account ID: {ACCOUNT_ID}</strong>, following the automated decline notification.</p>

  <p>Our initial application may have been filtered due to registering initially through an administrative email rather than our official domain address. We are confirming our credentials directly from our verified domain endpoint (<strong>partnership@heliatech.online</strong>).</p>

  <div class="meta-box">
    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 14px; text-transform: uppercase;">Platform Verification & Traffic Telemetry:</h4>
    <ul style="font-size: 13px;">
      <li><strong>Official Website:</strong> <a href="https://heliatech.online" class="highlight">https://heliatech.online</a></li>
      <li><strong>Account ID:</strong> {ACCOUNT_ID}</li>
      <li><strong>Official Corporate Email:</strong> partnership@heliatech.online</li>
      <li><strong>Business Model:</strong> High-intent technical B2B software audits, architectural teardowns, ROI benchmark duels, and buyer decision matrices.</li>
      <li><strong>Catalog Scale:</strong> Over 78 published in-depth software audits and 110 editorial masterclasses (>340 static pages).</li>
      <li><strong>Traffic Profile:</strong> High-value organic B2B audience (CTOs, software engineers, DevOps leads, and agency founders) primarily located in the United States, UK, and European Union.</li>
      <li><strong>Regulatory Compliance:</strong> Strict FTC affiliate disclosures on all articles, transparent Terms of Service, comprehensive Privacy Policy, zero coupon/incentivized traffic, and no trademark bidding.</li>
    </ul>
  </div>

  <p>We are actively looking to connect with relevant B2B SaaS, devtool, and enterprise cloud brands on the Impact marketplace (such as Canva, Semrush, HubSpot, and Hostinger) to include them in our technical comparisons and workflows.</p>

  <p>Could you please conduct a manual review of our domain (<strong>https://heliatech.online</strong>) and reinstate our publisher account <strong>#{ACCOUNT_ID}</strong>?</p>

  <p>Thank you for your consideration.</p>

  <div class="footer">
    <strong>HeliaTech Global Partnerships Team</strong><br>
    HeliaTech Media & Research Observatory<br>
    <a href="https://heliatech.online" class="highlight">https://heliatech.online</a> â€¢ partnership@heliatech.online
  </div>
</div>
</body>
</html>
"""

def send_appeal():
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "HeliaTech-Dispatcher/1.0"
    }

    payload = {
        "from": SENDER,
        "to": TO_RECIPIENTS,
        "cc": CC_RECIPIENTS,
        "reply_to": "partnership@heliatech.online",
        "subject": SUBJECT,
        "html": HTML_BODY
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
            print(f"[SUCCESS] Appeal email dispatched via Resend! Message ID: {data.get('id')}")
            return True, data.get("id")
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        print(f"[HTTP ERROR] Code {e.code}: {error_msg}")
        return False, error_msg
    except Exception as e:
        print(f"[ERROR] {e}")
        return False, str(e)

if __name__ == "__main__":
    success, res = send_appeal()
    sys.exit(0 if success else 1)
