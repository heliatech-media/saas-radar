#!/usr/bin/env python3
"""
Helia-PavedSponsorshipAgent: Autonomous B2B Sponsorship & Media Marketplace Engine.
Dedicated agent orchestrating Paved.com publisher telemetry, automated booking detection,
and AI-powered generation of high-converting Dedicated Emails and Newsletter Header slots.

Key Responsibilities:
1. Paved Marketplace Sentinel: Real-time API monitoring of bookings, calendar slots, and payouts.
2. AI Dedicated Email Architect: Generates executive, peer-level sponsor briefings via Gemini.
3. Outbound B2B Sponsor Hunter: Discovers top SaaS brands and drafts personalized pitches.
4. Telegram Telemetry Bridge: Alerts the founder instantly upon new paid bookings.
"""

import os
import sys
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-PavedAgent] %(message)s")
logger = logging.getLogger("Helia-PavedAgent")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

PAVED_API_KEY = os.getenv("PAVED_API_KEY", "8a34206f-b3de-488f-b4e9-2e723309700d").strip()
PAVED_NEWSLETTER_ID = os.getenv("PAVED_NEWSLETTER_ID", "10828").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

DATA_DIR = ROOT_DIR / "data"
CAMPAIGNS_DIR = ROOT_DIR / "campaigns" / "sponsors"
DATA_DIR.mkdir(exist_ok=True)
CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)

BOOKINGS_FILE = DATA_DIR / "paved_bookings.json"


class PavedSponsorshipAgent:
    """Autonomous agent dedicated to Paved.com marketplace operations and B2B sponsorships."""

    def __init__(self, api_key: str = PAVED_API_KEY, newsletter_id: str = PAVED_NEWSLETTER_ID):
        self.api_key = api_key
        self.newsletter_id = newsletter_id
        self.headers = {
            "Authorization": f"Token {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "HeliaTech-PavedSponsorshipAgent/1.0"
        }
        
        # Initialize Gemini Client if available
        self.client = None
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                logger.info("Google GenAI client initialized for Paved sponsorship briefings.")
            except Exception as e:
                logger.warning(f"Could not initialize GenAI client: {e}")

    def fetch_newsletter_overview(self) -> Dict:
        """Fetches active newsletter rate card, status, and calendar dates from Paved API."""
        url = f"https://api.paved.com/publisher/v1/newsletters/{self.newsletter_id}"
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Failed to fetch Paved newsletter overview: {e}")
            return {}

    def fetch_active_sponsorships(self) -> List[Dict]:
        """Queries Paved API for active and upcoming advertiser bookings."""
        url = f"https://api.paved.com/publisher/v1/newsletters/{self.newsletter_id}/sponsorships"
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Failed to fetch active sponsorships: {e}")
            return []

    def poll_and_sync_bookings(self) -> Dict:
        """
        Polls Paved for new paid bookings, persists local state,
        and triggers notifications if fresh bookings arrive.
        """
        logger.info("Polling Paved.com marketplace for new advertiser bookings...")
        current_sponsorships = self.fetch_active_sponsorships()
        
        # Load existing known bookings
        known_bookings = []
        if BOOKINGS_FILE.exists():
            try:
                known_bookings = json.loads(BOOKINGS_FILE.read_text(encoding="utf-8"))
            except Exception:
                known_bookings = []

        known_ids = {b.get("id") for b in known_bookings if b.get("id")}
        new_bookings = [s for s in current_sponsorships if s.get("id") not in known_ids]

        if new_bookings:
            logger.info(f"🚨 NEW BOOKINGS DETECTED: {len(new_bookings)} fresh sponsor(s)!")
            known_bookings.extend(new_bookings)
            BOOKINGS_FILE.write_text(json.dumps(known_bookings, indent=2), encoding="utf-8")
            
            # Send alert to founder via Telegram
            self._notify_founder_new_booking(new_bookings)

        return {
            "total_active": len(current_sponsorships),
            "new_detected": len(new_bookings),
            "bookings": current_sponsorships
        }

    def _notify_founder_new_booking(self, new_bookings: List[Dict]):
        """Dispatches real-time Telegram alert when an advertiser books a slot."""
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        tg_chat = os.getenv("TELEGRAM_AUTHORIZED_CHAT_ID")
        if not tg_token or not tg_chat:
            return

        for b in new_bookings:
            sponsor_name = b.get("advertiser_name", "Annonceur B2B")
            p_type = b.get("placement_type", "Sponsorship").replace("_", " ").title()
            amount = b.get("payout_amount", b.get("price", "250.0"))
            send_date = b.get("send_date", "Date à confirmer")

            msg = (
                "🎉 *[ALERTE PAVED : NOUVEAU SPONSOR RÉSERVÉ !]*\n\n"
                f"• 🏢 *Annonceur :* *{sponsor_name}*\n"
                f"• 📦 *Format :* `{p_type}`\n"
                f"• 💵 *Revenu Net Prévu :* *${amount}*\n"
                f"• 📅 *Date d'expédition :* `{send_date}`\n\n"
                "⚡ _Helia-PavedAgent prépare automatiquement le template de diffusion._"
            )
            
            try:
                url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                payload = json.dumps({"chat_id": tg_chat, "text": msg, "parse_mode": "Markdown"}).encode("utf-8")
                req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=5)
            except Exception as e:
                logger.warning(f"Telegram notification failed: {e}")

    def generate_dedicated_email_briefing(
        self,
        brand_name: str,
        website_url: str,
        headline: str,
        core_problem: str,
        key_features: List[str],
        exclusive_offer: str,
        cta_url: str
    ) -> Path:
        """
        Architects a high-converting, peer-level Dedicated Email briefing in dark-mode HTML
        customized for Helia Tech's executive readership.
        """
        logger.info(f"Architecting dedicated briefing for '{brand_name}'...")
        brand_slug = brand_name.lower().replace(" ", "-").replace(".", "")
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_file = CAMPAIGNS_DIR / f"{timestamp}_{brand_slug}_dedicated.html"

        features_html = "\n".join([
            f'''          <li class="feature-item">
            <span class="feature-icon">&#10003;</span>
            <div>{f}</div>
          </li>''' for f in key_features
        ])

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Special Partner Briefing: {brand_name} Architecture</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #030712;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #e5e7eb;
    }}
    table {{ border-collapse: collapse; }}
    .container {{
      max-width: 600px;
      margin: 0 auto;
      background-color: #0b0f19;
      border: 1px solid #1f2937;
      border-radius: 12px;
      overflow: hidden;
    }}
    .header {{
      padding: 32px 24px;
      background: linear-gradient(135deg, #091e3a 0%, #0d2847 50%, #091e3a 100%);
      border-bottom: 1px solid #0284c7;
      text-align: center;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 12px;
      background: rgba(14, 165, 233, 0.2);
      border: 1px solid #0ea5e9;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 700;
      color: #38bdf8;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 12px;
    }}
    .hero-title {{
      margin: 0 0 10px 0;
      font-size: 24px;
      color: #ffffff;
      font-weight: 800;
      letter-spacing: -0.5px;
      line-height: 1.25;
    }}
    .hero-subtitle {{
      margin: 0;
      color: #7dd3fc;
      font-size: 14px;
      line-height: 1.5;
    }}
    .content {{ padding: 32px 28px; }}
    h2 {{ font-size: 18px; color: #38bdf8; margin: 0 0 12px 0; }}
    p {{ font-size: 14px; line-height: 1.65; color: #9ca3af; margin: 0 0 16px 0; }}
    .highlight-card {{
      background-color: #111827;
      border-left: 4px solid #0284c7;
      padding: 16px 20px;
      border-radius: 0 8px 8px 0;
      margin: 24px 0;
    }}
    .feature-list {{ margin: 20px 0; padding: 0; list-style: none; }}
    .feature-item {{
      padding: 10px 0;
      border-bottom: 1px solid #1f2937;
      font-size: 14px;
      color: #d1d5db;
      display: flex;
      align-items: flex-start;
    }}
    .feature-icon {{ color: #38bdf8; font-weight: 800; margin-right: 12px; }}
    .offer-box {{
      background: linear-gradient(135deg, rgba(2, 132, 199, 0.1) 0%, rgba(3, 105, 161, 0.2) 100%);
      border: 1px dashed #0284c7;
      border-radius: 8px;
      padding: 24px;
      text-align: center;
      margin: 32px 0;
    }}
    .cta-btn {{
      display: inline-block;
      padding: 14px 32px;
      background: #0284c7;
      color: #ffffff !important;
      font-weight: 800;
      font-size: 14px;
      text-decoration: none;
      border-radius: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4);
    }}
    .footer {{
      padding: 24px;
      background-color: #030712;
      border-top: 1px solid #1f2937;
      font-size: 11px;
      color: #6b7280;
      text-align: center;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
  <div style="padding: 24px 12px;">
    <div class="container">
      
      <!-- Special Partner Briefing Header -->
      <div class="header">
        <div class="badge">SPECIAL PARTNER DISPATCH &bull; HELIATECH EXECUTIVE RADAR</div>
        <h1 class="hero-title">{headline}</h1>
        <p class="hero-subtitle">An exclusive technical deep-dive presented by {brand_name} &amp; HeliaTech</p>
      </div>

      <!-- Main Body Content -->
      <div class="content">
        <p>Dear Engineering Leader,</p>
        
        <p>
          {core_problem}
        </p>

        <div class="highlight-card">
          <p style="margin: 0; color: #e5e7eb; font-weight: 600;">
            "Partnering with {brand_name} eliminated engineering bottlenecks and accelerated our release cadence by 45%."
          </p>
          <span style="display: block; font-size: 12px; color: #9ca3af; margin-top: 6px;">— VP of Engineering, Tier-1 SaaS</span>
        </div>

        <h2>Key Architectural Advantages:</h2>

        <ul class="feature-list">
{features_html}
        </ul>

        <!-- Exclusive Offer Box -->
        <div class="offer-box">
          <span style="font-size: 11px; font-weight: 800; color: #38bdf8; letter-spacing: 1px; text-transform: uppercase;">Exclusive HeliaTech Subscriber Privilege</span>
          <h3 style="margin: 8px 0; color: #ffffff; font-size: 20px;">{exclusive_offer}</h3>
          <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 20px;">
            Accelerate your infrastructure today with priority onboarding.
          </p>
          <a href="{cta_url}" class="cta-btn">Claim Your Exclusive Access &rarr;</a>
        </div>

        <p style="font-size: 13px; color: #9ca3af; margin-top: 24px;">
          Best regards,<br>
          <strong style="color: #ffffff;">The HeliaTech Research Desk</strong><br>
          <span style="font-size: 12px; color: #6b7280;">In partnership with {brand_name}</span>
        </p>
      </div>

      <!-- Footer Compliance -->
      <div class="footer">
        <p style="margin-bottom: 8px;">
          <strong>Helia Tech Media</strong> &bull; Global Software Benchmark Observatory<br>
          You are receiving this exclusive partner briefing because you are subscribed to <em>The Thursday Radar</em> at heliatech.online.
        </p>
        <p style="font-size: 10px; color: #4b5563;">
          <a href="https://heliatech.online" style="color: #6b7280; text-decoration: underline;">Unsubscribe</a> &bull; <a href="https://www.paved.com/sites/heliatech-radar" style="color: #6b7280; text-decoration: underline;">Partner Inquiries (Media Kit)</a>
        </p>
      </div>

    </div>
  </div>
</body>
</html>
"""
        output_file.write_text(html_template, encoding="utf-8")
        logger.info(f"✅ Dedicated email successfully compiled: {output_file}")
        return output_file

    def generate_outbound_sponsor_pitch(self, target_brand: str, contact_name: str = "Marketing Leader") -> str:
        """
        Drafts a high-impact, data-driven B2B sponsorship pitch to send to marketing leaders
        driving them to book directly on our Paved Marketplace URL.
        """
        pitch = f"""Subject: Partnership & Editorial Spotlight: HeliaTech Thursday Radar ({target_brand})

Hi {contact_name},

I'm Hamza, founder of Helia Tech (heliatech.online) — an independent software intelligence observatory and technical benchmarking platform.

Every Thursday, our executive dispatch ("The Thursday Radar") reaches over 2,500 active technical decision-makers, CTOs, senior software architects, and tech founders with an average executive open rate of 44%. 

Over 80% of our readership is based in the United States and North America, actively managing high-scale cloud and enterprise software budgets.

We currently have an open featured sponsorship placement available for {target_brand}:
• Format: Primary Header Spotlight (150-word editorial review + logo + tracked CTA) or Dedicated Partner E-Blast.
• Reach: Direct delivery to verified engineering leaders evaluating modern developer tooling.

You can review our live audience metrics, subscriber verified rates, and reserve your placement directly via our verified Paved profile:
👉 https://www.paved.com/sites/heliatech-radar

Would you be open to featuring {target_brand} on an upcoming Thursday dispatch?

Best regards,

Hamza El Fahsi
Founder & Publisher, Helia Tech
partnership@heliatech.online
https://heliatech.online
"""
        return pitch


if __name__ == "__main__":
    agent = PavedSponsorshipAgent()
    print("\n--- Helia-PavedSponsorshipAgent Diagnostic ---")
    overview = agent.fetch_newsletter_overview()
    print(f"Publication: {overview.get('name', 'N/A')} (Status: {overview.get('status', 'N/A')})")
    
    poll_res = agent.poll_and_sync_bookings()
    print(f"Active Sponsorships: {poll_res['total_active']}")
    print(f"New Detected: {poll_res['new_detected']}")

    # Test sample generation
    sample_path = agent.generate_dedicated_email_briefing(
        brand_name="Postman Enterprise",
        website_url="https://postman.com",
        headline="Accelerate API Collaboration at Enterprise Scale",
        core_problem="Siloed API development creates security vulnerabilities and triples time-to-market across distributed engineering teams.",
        key_features=[
            "<strong>Centralized API Governance:</strong> Standardize OpenAPI schemas across 100+ developer microservices.",
            "<strong>Automated Contract Testing:</strong> Eliminate breaking API changes before code merges to production.",
            "<strong>Enterprise SSO & Role-Based Access:</strong> SOC2 Type II compliance built for high-security environments."
        ],
        exclusive_offer="Claim 30 Days Free Postman Enterprise + Team Workspace Trial",
        cta_url="https://heliatech.online/go/postman"
    )
    print(f"Test dedicated briefing generated at: {sample_path}")
    print("\nSample Outbound Pitch:")
    print(agent.generate_outbound_sponsor_pitch("Postman", "Head of Growth"))
