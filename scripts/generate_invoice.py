#!/usr/bin/env python3
"""
HeliaTech Enterprise B2B Invoice Generator
Generates clean, professional, PDF-printable commercial invoices for HeliaTech sponsors.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT_DIR / "templates" / "invoices" / "commercial_invoice.html"
OUTPUT_DIR = ROOT_DIR / "reports" / "invoices"

TIERS_CONFIG = {
    "newsletter": {
        "title": "The Thursday Radar — Exclusive Solo Sponsorship",
        "description": "Exclusive solo sponsor placement in HeliaTech's executive weekly briefing. Includes 120-word executive pitch, official brand logo, and primary Call-to-Action button delivered to 14,000+ verified CTOs, founders, and engineering leaders.",
        "amount": "250.00",
        "period": "Next Available Thursday (09:00 AM EST)"
    },
    "spotlight": {
        "title": "Category Partner Spotlight (30 Days)",
        "description": "Featured partner banner and promotional credit integration across all comparative duels and articles in the designated software vertical on HeliaTech.online. Includes do-follow backlinks and monthly conversion analytics.",
        "amount": "400.00",
        "period": "30-Day Monthly Rotation"
    },
    "masterclass": {
        "title": "Technical Masterclass & Architecture Blueprint",
        "description": "Permanent long-form engineering tutorial with native interactive Mermaid architecture diagrams, verified Docker Compose deployment files, and code-level integration patterns. Permanently indexed on search engines.",
        "amount": "950.00",
        "period": "Permanent Indexation"
    }
}

DEFAULT_BANKING = {
    "bank_beneficiary": "HeliaTech Research & Media Division",
    "bank_name": "International Business Clearing Bank",
    "bank_iban": "US89 BANA 0001 2345 6789 01",
    "bank_swift": "BANAUS33XXX",
    "paypal_email": "partnership@heliatech.online",
    "stripe_payment_url": "https://buy.stripe.com/heliatech_sponsor_checkout"
}

def generate_invoice(
    client_company: str,
    client_contact: str = "Finance & Marketing Desk",
    client_email: str = "billing@client.com",
    client_address: str = "San Francisco, CA, United States",
    client_tax_id: str = "N/A (International)",
    tier: str = "newsletter",
    custom_title: str = None,
    custom_desc: str = None,
    custom_amount: str = None,
    custom_period: str = None,
    invoice_number: str = None,
    output_filename: str = None
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    inv_num = invoice_number or f"HT-{now.strftime('%Y%m')}-{now.strftime('%d%H%M')}"
    inv_date = now.strftime("%B %d, %Y")
    due_date = (now + timedelta(days=15)).strftime("%B %d, %Y")

    tier_info = TIERS_CONFIG.get(tier, TIERS_CONFIG["newsletter"])
    item_title = custom_title or tier_info["title"]
    item_desc = custom_desc or tier_info["description"]
    amount = custom_amount or tier_info["amount"]
    period = custom_period or tier_info["period"]

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    replacements = {
        "invoice_number": inv_num,
        "invoice_status": "PENDING PAYMENT",
        "invoice_date": inv_date,
        "due_date": due_date,
        "payment_terms": "Due Upon Receipt (Net 15)",
        "currency": "USD",
        "client_company": client_company,
        "client_contact": client_contact,
        "client_email": client_email,
        "client_address": client_address,
        "client_tax_id": client_tax_id,
        "item_title": item_title,
        "item_description": item_desc,
        "item_period": period,
        "amount": amount,
        "bank_beneficiary": DEFAULT_BANKING["bank_beneficiary"],
        "bank_name": DEFAULT_BANKING["bank_name"],
        "bank_iban": DEFAULT_BANKING["bank_iban"],
        "bank_swift": DEFAULT_BANKING["bank_swift"],
        "paypal_email": DEFAULT_BANKING["paypal_email"],
        "stripe_payment_url": DEFAULT_BANKING["stripe_payment_url"]
    }

    for key, value in replacements.items():
        html = html.replace("{{" + key + "}}", str(value))

    safe_name = "".join(c for c in client_company if c.isalnum() or c in ("-", "_")).lower()
    out_name = output_filename or f"invoice_{inv_num}_{safe_name}.html"
    out_path = OUTPUT_DIR / out_name

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[+] Invoice generated successfully: {out_path}")
    return out_path

def main():
    parser = argparse.ArgumentParser(description="Generate a professional B2B invoice for HeliaTech sponsors.")
    parser.add_argument("--client", required=True, help="Client/Company name (e.g. 'Resend Inc.')")
    parser.add_argument("--contact", default="Partnerships Team", help="Contact person or department")
    parser.add_argument("--email", default="finance@company.com", help="Client billing email")
    parser.add_argument("--tier", choices=["newsletter", "spotlight", "masterclass"], default="newsletter", help="Sponsorship package tier")
    parser.add_argument("--amount", default=None, help="Custom amount in USD")
    parser.add_argument("--period", default=None, help="Custom service period / issue number")
    args = parser.parse_args()

    generate_invoice(
        client_company=args.client,
        client_contact=args.contact,
        client_email=args.email,
        tier=args.tier,
        custom_amount=args.amount,
        custom_period=args.period
    )

if __name__ == "__main__":
    main()
