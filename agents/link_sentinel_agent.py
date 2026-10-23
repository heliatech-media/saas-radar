"""
Helia-LinkSentinel: Autonomous Affiliate & Edge Redirect Health Guardian.
Periodically audits all 302 destination URLs in site/public/_redirects.
Detects broken tracking links, 404s, domain expirations, or partner network drops,
and alerts the Founder immediately via Telegram to prevent revenue leakage.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import requests
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-LinkSentinel] %(message)s")
logger = logging.getLogger("Helia-LinkSentinel")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from agents.notifier_agent import NotifierAgent

REDIRECTS_PATH = ROOT_DIR / "site" / "public" / "_redirects"
HEALTH_REPORT_PATH = ROOT_DIR / "reports" / "link_health_audit.json"


class LinkSentinelAgent:
    """
    Helia-LinkSentinel: Detects dead affiliate hops before they cost money.
    """
    def __init__(self):
        self.notifier = NotifierAgent()
        HEALTH_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    def audit_all_redirects(self) -> Dict:
        """
        Pings every destination URL in _redirects and validates HTTP response codes.
        """
        logger.info("🛡️ Initiating full-spectrum Affiliate Link Health Audit...")

        if not REDIRECTS_PATH.exists():
            logger.error(f"_redirects file not found at {REDIRECTS_PATH}")
            return {"status": "ERROR", "message": "_redirects missing"}

        links_to_check = []
        for line in REDIRECTS_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("/go/") and "http" in line:
                parts = line.split()
                slug = parts[0].replace("/go/", "")
                target_url = parts[1]
                links_to_check.append((slug, target_url))

        logger.info(f"Pinging {len(links_to_check)} affiliate destinations...")

        audit_results = []
        broken_links = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        for slug, target in links_to_check:
            try:
                # Use head or get with redirect follow, 7s timeout
                res = requests.get(target, headers=headers, timeout=7, allow_redirects=True)
                code = res.status_code
                is_healthy = code in (200, 301, 302, 307, 308, 403) # 403 is often bot-shield but page is live
                
                result = {
                    "slug": slug,
                    "target_url": target,
                    "final_url": res.url,
                    "status_code": code,
                    "healthy": is_healthy
                }
                audit_results.append(result)

                if not is_healthy and code in (404, 500, 502, 503):
                    broken_links.append(result)
                    logger.warning(f"⚠️ Potentially broken link detected: /go/{slug} -> HTTP {code}")

            except Exception as e:
                # Network timeout or DNS failure
                result = {
                    "slug": slug,
                    "target_url": target,
                    "final_url": "FAILED",
                    "status_code": 0,
                    "healthy": False,
                    "error": str(e)
                }
                audit_results.append(result)
                broken_links.append(result)
                logger.warning(f"⚠️ Connection failure for /go/{slug}: {e}")

        healthy_count = len(audit_results) - len(broken_links)
        health_rate = round((healthy_count / max(1, len(audit_results))) * 100, 1)

        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_links_audited": len(audit_results),
            "healthy_links": healthy_count,
            "broken_links_count": len(broken_links),
            "health_rate": f"{health_rate}%",
            "broken_links": broken_links,
            "audit_details": audit_results
        }

        with open(HEALTH_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Alert founder via Telegram if broken links detected
        if broken_links:
            broken_slugs = ", ".join([b["slug"] for b in broken_links])
            alert_msg = (
                f"🚨 *ALERTE LIENS MORTS DÉTECTÉS !*\n\n"
                f"Helia-LinkSentinel a identifié {len(broken_links)} lien(s) d'affiliation en anomalie :\n"
                f"• `{broken_slugs}`\n\n"
                f"Vérifiez le rapport : `reports/link_health_audit.json`"
            )
            try:
                self.notifier.send_notification(
                    title="Alerte Lien Mort Détecté",
                    message=alert_msg,
                    category="ALERT"
                )
            except Exception:
                pass
        else:
            logger.info(f"✅ Tous les {healthy_count} liens d'affiliation sont sains et opérationnels (100% OK).")

        return report


if __name__ == "__main__":
    sentinel = LinkSentinelAgent()
    res = sentinel.audit_all_redirects()
    print(f"\n--- Helia-LinkSentinel Summary ---")
    print(f"Total Links Checked: {res['total_links_audited']}")
    print(f"Health Rate: {res['health_rate']}")
    print(f"Broken Links: {res['broken_links_count']}")
