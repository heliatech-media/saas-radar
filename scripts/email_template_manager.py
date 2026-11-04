#!/usr/bin/env python3
"""
HeliaTech Email Template Manager & Dispatcher
Renders, tests, and dispatches production HTML email templates via Resend.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"
DEFAULT_TEST_EMAIL = "director@heliatech.online"
SENDER = "HeliaTech <partnership@heliatech.online>"

SAMPLE_DATA = {
    "welcome": {
        "email": DEFAULT_TEST_EMAIL,
        "unsubscribe_url": "https://heliatech.online/unsubscribe?email=" + DEFAULT_TEST_EMAIL,
    },
    "weekly": {
        "issue_number": "042",
        "publish_date": "Thursday, Nov 5, 2026",
        "issue_headline": "The Great SaaS Consolidation: Why Engineering Teams Are Ditching Fragmented 2024 Stacks",
        "issue_title": "Issue #042: The Great SaaS Consolidation",
        "executive_summary": "This week, we evaluated over 120 workflow integrations across Make, Resend, and Supabase to calculate true developer velocity. Here is where the enterprise market is migrating.",
        "teardown_tool_name": "Resend",
        "teardown_tool_verdict_title": "The Death of Legacy SMTP & The Rise of React Email",
        "teardown_summary": "Legacy email infrastructure burns an average of 40 engineering hours per month in SMTP debugging and template rendering failures. Resend's component-driven DX cuts integration cycles from 3 days to 12 minutes.",
        "score_roi": "96%",
        "score_friction": "Low (9/10)",
        "score_overall": "9.8 / 10",
        "teardown_review_url": "https://heliatech.online/reviews/resend/",
        "duel_title": "Make.com vs Zapier (2026 Enterprise Showdown)",
        "duel_takeaway": "When scaling past 100,000 automated operations per month, Zapier's pricing model acts as a direct margin penalty compared to Make's visual router execution.",
        "duel_winner_reason": "Make delivers 4.8x cost savings at scale with vastly superior branch logic control.",
        "duel_url": "https://heliatech.online/versus/make-vs-zapier/",
        "deal_headline": "Make.com: 3 Months Free Pro Tier + 10,000 Operations",
        "deal_description": "Exclusive partnership access for HeliaTech subscribers to unlock high-concurrency enterprise automation pipelines with zero upfront commitment.",
        "deal_hop_link": "https://heliatech.online/go/make",
        "email": DEFAULT_TEST_EMAIL,
        "unsubscribe_url": "https://heliatech.online/unsubscribe?email=" + DEFAULT_TEST_EMAIL,
    },
    "pitch": {
        "contact_name": "Alex",
        "tool_name": "Supabase",
        "competitor_name": "Firebase",
        "monthly_reach": "6,500+",
    },
    "cfo_memo": {
        "annual_savings": "$18,450 / yr",
        "hours_saved": "64 hrs / mo",
        "recommended_stack": "Make.com + Resend + Supabase + Cursor",
        "memo_dashboard_link": "https://heliatech.online/calculator/",
    }
}

TEMPLATE_FILES = {
    "welcome": "welcome_briefing.html",
    "weekly": "weekly_confidential.html",
    "pitch": "sponsor_pitch.html",
    "cfo_memo": "cfo_memo_delivery.html",
}

def render_template(template_name: str, context: dict = None) -> str:
    filename = TEMPLATE_FILES.get(template_name)
    if not filename:
        raise ValueError(f"Unknown template: {template_name}. Available: {list(TEMPLATE_FILES.keys())}")

    filepath = TEMPLATES_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Template file not found at {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    data = SAMPLE_DATA.get(template_name, {}).copy()
    if context:
        data.update(context)

    for key, value in data.items():
        placeholder = "{{" + key + "}}"
        html = html.replace(placeholder, str(value))

    return html

def send_test_email(template_name: str, to_email: str = DEFAULT_TEST_EMAIL):
    from send_email import send_email

    subjects = {
        "welcome": "⚡ [HELIATECH] Your Executive SaaS Briefing & ROI Intelligence Access",
        "weekly": "⚡ [THE RADAR #042] The Great SaaS Consolidation Teardown",
        "pitch": "🤝 Partnership Inquiry: Supabase x HeliaTech Media Radar",
        "cfo_memo": "📊 Your HeliaTech CFO Board Memo & Optimization Audit",
    }

    html = render_template(template_name, {"email": to_email})
    subject = subjects.get(template_name, f"HeliaTech Test: {template_name.capitalize()}")

    print(f"[*] Sending test email '{template_name}' to {to_email}...")
    success = send_email(to_email, subject, html, sender=SENDER)
    if success:
        print(f"[+] Test email successfully delivered!")
    else:
        print(f"[-] Failed to send test email.")
    return success

def main():
    parser = argparse.ArgumentParser(description="HeliaTech Email Template Manager")
    parser.add_argument("--list", action="store_true", help="List available templates")
    parser.add_argument("--render", type=str, choices=list(TEMPLATE_FILES.keys()), help="Render template to console or preview file")
    parser.add_argument("--test", type=str, choices=list(TEMPLATE_FILES.keys()) + ["all"], help="Send a live test email via Resend")
    parser.add_argument("--to", type=str, default=DEFAULT_TEST_EMAIL, help="Recipient for test emails")
    args = parser.parse_args()

    if args.list:
        print("\n=== HELIATECH EMAIL TEMPLATES CATALOG ===")
        for key, fname in TEMPLATE_FILES.items():
            print(f"  • {key:<12} -> {fname}")
        print("\n")
        return

    if args.render:
        html = render_template(args.render)
        preview_file = TEMPLATES_DIR / f"preview_{args.render}.html"
        with open(preview_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[+] Rendered preview saved to: {preview_file}")
        return

    if args.test:
        if args.test == "all":
            for t in TEMPLATE_FILES.keys():
                send_test_email(t, args.to)
        else:
            send_test_email(args.test, args.to)
        return

    parser.print_help()

if __name__ == "__main__":
    main()
