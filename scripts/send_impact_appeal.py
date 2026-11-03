#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if not RESEND_API_KEY:
    print("[ERROR] RESEND_API_KEY missing")
    sys.exit(1)

sender = "Hamza El Fahsi • HeliaTech <partnership@heliatech.online>"
to_recipients = ["support@impact.com"]
cc_recipients = ["hamzaelfahsi@gmail.com"]

subject = "Publisher Application Review & Manual Verification: HeliaTech Media (https://heliatech.online)"

html_body = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b; line-height: 1.6; }
  .container { max-width: 640px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; }
  .header { border-bottom: 2px solid #0284c7; padding-bottom: 12px; margin-bottom: 20px; }
  .badge { display: inline-block; padding: 4px 10px; background: #e0f2fe; color: #0369a1; border-radius: 9999px; font-size: 12px; font-weight: bold; text-transform: uppercase; }
  .meta-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin: 20px 0; }
  .meta-box ul { margin: 0; padding-left: 20px; }
  .footer { margin-top: 30px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 13px; color: #64748b; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <span class="badge">HeliaTech Media • Official Publisher Appeal</span>
    <h2 style="margin: 8px 0 0 0; color: #0f172a;">Application Review & Manual Verification Request</h2>
  </div>

  <p>Dear Impact.com Publisher Onboarding & Review Team,</p>

  <p>I am writing to formally request a manual human review of our publisher application for <strong>HeliaTech Media</strong> (<a href="https://heliatech.online" style="color: #0284c7;">https://heliatech.online</a>).</p>

  <p>Our initial automated application was declined, likely triggered by using our administrative Gmail address during sign-up rather than our corporate domain address. We are resubmitting our credentials directly from our verified domain endpoint (<strong>partnership@heliatech.online</strong>).</p>

  <div class="meta-box">
    <h4 style="margin: 0 0 10px 0; color: #0f172a;">Platform Overview & Verification Telemetry:</h4>
    <ul>
      <li><strong>Live Platform:</strong> <a href="https://heliatech.online" style="color: #0284c7;">https://heliatech.online</a></li>
      <li><strong>Official Corporate Email:</strong> partnership@heliatech.online</li>
      <li><strong>Publisher Profile:</strong> HeliaTech Media</li>
      <li><strong>Business Model:</strong> In-depth B2B SaaS benchmarks, software architectural teardowns, head-to-head duels, and buyer decision matrices.</li>
      <li><strong>Catalog Scale:</strong> Over 240+ fully indexed, original technical articles, duels, and software reviews.</li>
      <li><strong>Monthly Traffic:</strong> 12,000+ monthly pageviews, with over 80% of our reader base originating from the United States and Europe across software engineers, CTOs, and RevOps leaders.</li>
      <li><strong>Compliance:</strong> Zero cookie tracking, fully compliant with GDPR/CCPA, clear editorial disclosures, and established ads.txt / security protocols.</li>
    </ul>
  </div>

  <p>We are actively positioned to promote leading enterprise software, devtools, and cloud infrastructure partners on the Impact marketplace (such as Canva, HubSpot, Semrush, and Hostinger).</p>

  <p>Could you please conduct a manual review of our domain and grant approval for our publisher account under <strong>partnership@heliatech.online</strong>?</p>

  <p>Thank you for your assistance and review.</p>

  <div class="footer">
    <strong>Hamza El Fahsi</strong><br>
    Founder & Head of Operations<br>
    HeliaTech Media Observatory<br>
    <a href="https://heliatech.online" style="color: #0284c7;">https://heliatech.online</a> • partnership@heliatech.online
  </div>
</div>
</body>
</html>
"""

url = "https://api.resend.com/emails"
headers = {
    "Authorization": f"Bearer {RESEND_API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "HeliaTech-Dispatcher/1.0"
}

payload = {
    "from": sender,
    "to": to_recipients,
    "cc": cc_recipients,
    "reply_to": "partnership@heliatech.online",
    "subject": subject,
    "html": html_body
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
        print(f"[SUCCESS] Appeal email dispatched via Resend! ID: {data.get('id')}")
except urllib.error.HTTPError as e:
    print(f"[HTTP ERROR] Code {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"[ERROR] {e}")
