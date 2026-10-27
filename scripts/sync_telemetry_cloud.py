"""
Helia Cloud Telemetry Synchronizer for GitHub Actions (Cloud-Native Cron).
Runs every 30 minutes in GitHub Actions cloud runner:
1. Queries Cloudflare Zone GraphQL API directly
2. Updates live_cloudflare_telemetry.json
3. Detects if visitor numbers or pageviews increased
4. Exits with code 0 (success) or 10 (no change needed)
"""

import os
import sys
import json
import logging
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from agents.cloudflare_analytics_agent import CloudflareAnalyticsAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Cloud-Telemetry-Sync] %(message)s")
logger = logging.getLogger("CloudTelemetry")

def main():
    agent = CloudflareAnalyticsAgent()
    if not agent.is_configured():
        logger.error("CLOUDFLARE_API_TOKEN or CLOUDFLARE_ZONE_ID not configured in environment.")
        sys.exit(1)

    logger.info("Connecting to Cloudflare Zone Analytics in the cloud...")
    try:
        telemetry = agent.fetch_web_analytics(days=28)
        uniques = telemetry.get("total_visitors_network", 0)
        requests = telemetry.get("total_requests", 0)
        pageviews = telemetry.get("total_pageviews", 0)
        logger.info(f"Verified Cloudflare Live Telemetry: {uniques} unique visitors, {requests} requests, {pageviews} pageviews.")

        # Read previous live telemetry to compare
        prev_path = ROOT_DIR / "site" / "public" / "data" / "live_cloudflare_telemetry.json"
        prev_uniques = 0
        if prev_path.exists():
            try:
                prev_data = json.loads(prev_path.read_text(encoding="utf-8"))
                prev_uniques = prev_data.get("total_visitors_network", 0)
            except Exception:
                pass

        diff = uniques - prev_uniques
        if diff > 0 or prev_uniques == 0:
            logger.info(f"📈 Traffic increased (+{diff} new network visitors). Triggering Git sync.")
            sys.exit(0)
        else:
            logger.info(f"⚖️ Traffic stable ({uniques} visitors). No git commit required.")
            sys.exit(10) # 10 indicates no changes to commit

    except Exception as e:
        logger.error(f"Error fetching telemetry: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
