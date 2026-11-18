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
    "bank_name": "International Commercial Bank (SEPA / SWIFT / ACH)",
    "bank_iban": "US89 BANA 0001 2345 6789 01",
    "bank_swift": "BANAUS33XXX",
    "paypal_email": "partnership@heliatech.online",
    "paypal_payment_url": "https://paypal.me/heliatech"
}

def generate_invoice(
    client_company: str,
    client_contact: str = "Finance & Marketing Desk",
    client_email: str = "billing@client.com",
    client_address: str = "San Francisco, CA, United States",
    client_tax_id: str = "N/A (International)",
    tier: str = "newsletter",
    payment_method: str = "wire",
    custom_title: str = None,
    custom_desc: str = None,
    custom_amount: str = None,
    custom_period: str = None,
    invoice_number: str = None,
    bank_beneficiary: str = None,
    bank_name: str = None,
    bank_iban: str = None,
    bank_swift: str = None,
    paypal_email: str = None,
    paypal_payment_url: str = None,
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

    # Dynamic single payment method chosen by the client
    method_normalized = (payment_method or "wire").strip().lower()
    actual_paypal_email = paypal_email or DEFAULT_BANKING["paypal_email"]
    actual_paypal_url = paypal_payment_url or DEFAULT_BANKING["paypal_payment_url"]
    actual_bank_beneficiary = bank_beneficiary or DEFAULT_BANKING["bank_beneficiary"]
    actual_bank_name = bank_name or DEFAULT_BANKING["bank_name"]
    actual_bank_iban = bank_iban or DEFAULT_BANKING["bank_iban"]
    actual_bank_swift = bank_swift or DEFAULT_BANKING["bank_swift"]

    if method_normalized in ["paypal", "pp"]:
        payment_method_label = "PayPal Business Instant Transfer"
        payment_instructions_section = f"""<div class="payment-section">
      <div class="payment-title">⚡ INSTRUCTIONS DE RÈGLEMENT / PAYMENT INSTRUCTIONS (PAYPAL BUSINESS)</div>
      
      <div style="background: #ffffff; padding: 22px 24px; border-radius: 12px; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between; gap: 24px;">
        <div style="flex: 1;">
          <div style="font-weight: 800; font-size: 14px; color: #0f172a; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 18px;">🅿️</span> Règlement par Compte PayPal Business
          </div>
          <div style="font-size: 12px; line-height: 1.8; color: #334155;">
            <strong>Compte PayPal destinataire :</strong> <span class="mono" style="font-weight: 800; color: #0284c7; font-size: 13px;">{actual_paypal_email}</span><br/>
            <strong>Type de transfert :</strong> Biens &amp; Services professionnels B2B<br/>
            <strong>Référence obligatoire :</strong> <span class="mono" style="background: #f1f5f9; padding: 3px 8px; border-radius: 4px; font-weight: 800; color: #0f172a;">Facture #{inv_num}</span>
          </div>
        </div>
        <div style="text-align: right;">
          <a href="{actual_paypal_url}" target="_blank" class="pay-btn" style="display: inline-block; background: #0070ba; color: #ffffff; text-decoration: none; padding: 12px 26px; border-radius: 8px; font-weight: 800; font-size: 12px; letter-spacing: 0.05em; box-shadow: 0 4px 12px rgba(0, 112, 186, 0.25);">
            Régler ${amount} via PayPal.me ➔
          </a>
          <div style="font-size: 11px; color: #64748b; margin-top: 6px;">Confirmation et reçu comptable instantanés</div>
        </div>
      </div>
    </div>"""
    else:
        # Default: Virement Bancaire (Bank Wire Transfer)
        payment_method_label = "Virement Bancaire (Bank Wire / SEPA / SWIFT)"
        payment_instructions_section = f"""<div class="payment-section">
      <div class="payment-title">⚡ INSTRUCTIONS DE RÈGLEMENT / PAYMENT INSTRUCTIONS (BANK WIRE TRANSFER)</div>
      
      <div style="background: #ffffff; padding: 22px 24px; border-radius: 12px; border: 1px solid #e2e8f0;">
        <div style="font-weight: 800; font-size: 14px; color: #0f172a; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 18px;">🏛️</span> Virement Bancaire International (SEPA / SWIFT / ACH)
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 12px; line-height: 1.8; color: #334155;">
          <div>
            <strong>Bénéficiaire :</strong> <span class="mono" style="font-weight: 600;">{actual_bank_beneficiary}</span><br/>
            <strong>Établissement bancaire :</strong> <span class="mono">{actual_bank_name}</span><br/>
            <strong>Devises acceptées :</strong> <span class="mono">USD ($) &amp; EUR (€)</span>
          </div>
          <div>
            <strong>IBAN / Compte :</strong> <span class="mono" style="font-weight: 800; color: #0284c7; font-size: 13px;">{actual_bank_iban}</span><br/>
            <strong>Code BIC / SWIFT :</strong> <span class="mono" style="font-weight: 700;">{actual_bank_swift}</span><br/>
            <strong>Motif obligatoire du virement :</strong> <span class="mono" style="background: #f1f5f9; padding: 3px 8px; border-radius: 4px; font-weight: 800; color: #0f172a;">Facture #{inv_num}</span>
          </div>
        </div>
        <div style="margin-top: 14px; padding-top: 10px; border-top: 1px dashed #e2e8f0; font-size: 11px; color: #64748b;">
          ℹ️ Merci d'indiquer impérativement le numéro de facture <strong>#{inv_num}</strong> dans l'ordre de virement pour valider votre parution.
        </div>
      </div>
    </div>"""

    replacements = {
        "invoice_number": inv_num,
        "invoice_status": "PENDING PAYMENT",
        "invoice_date": inv_date,
        "due_date": due_date,
        "payment_terms": "Due Upon Receipt (Net 15)",
        "payment_method_label": payment_method_label,
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
        "payment_instructions_section": payment_instructions_section
    }

    for key, value in replacements.items():
        html = html.replace("{{" + key + "}}", str(value))

    safe_name = "".join(c for c in client_company if c.isalnum() or c in ("-", "_")).lower()
    method_slug = "paypal" if method_normalized in ["paypal", "pp"] else "wire"
    out_name = output_filename or f"invoice_{inv_num}_{safe_name}_{method_slug}.html"
    out_path = OUTPUT_DIR / out_name

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[+] Invoice generated successfully ({payment_method_label}): {out_path}")
    return out_path

def main():
    parser = argparse.ArgumentParser(description="Generate a professional B2B invoice for HeliaTech sponsors with the client's chosen payment method.")
    parser.add_argument("--client", required=True, help="Client/Company name (e.g. 'Resend Inc.')")
    parser.add_argument("--contact", default="Partnerships Team", help="Contact person or department")
    parser.add_argument("--email", default="finance@company.com", help="Client billing email")
    parser.add_argument("--tier", choices=["newsletter", "spotlight", "masterclass"], default="newsletter", help="Sponsorship package tier")
    parser.add_argument("--method", choices=["wire", "paypal", "virement"], default="wire", help="Payment method chosen by client: 'wire' (Bank wire) or 'paypal'")
    parser.add_argument("--amount", default=None, help="Custom amount in USD")
    parser.add_argument("--period", default=None, help="Custom service period / issue number")
    parser.add_argument("--iban", default=None, help="Custom IBAN or Account Number")
    parser.add_argument("--swift", default=None, help="Custom SWIFT/BIC")
    parser.add_argument("--paypal-email", default=None, help="Custom PayPal email")
    parser.add_argument("--paypal-url", default=None, help="Custom PayPal.me payment URL")
    args = parser.parse_args()

    generate_invoice(
        client_company=args.client,
        client_contact=args.contact,
        client_email=args.email,
        tier=args.tier,
        payment_method=args.method,
        custom_amount=args.amount,
        custom_period=args.period,
        bank_iban=args.iban,
        bank_swift=args.swift,
        paypal_email=args.paypal_email,
        paypal_payment_url=args.paypal_url
    )

if __name__ == "__main__":
    main()
