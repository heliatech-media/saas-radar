"""
Helia 24/7 Autonomous Daemon: Zero-Human-Intervention Autonomous Growth Engine.
Continuously runs HeliaTech's AI fleet:
- Discovers trending B2B software
- Hunts and extracts affiliate/partner links autonomously
- Authors technical teardowns and comprehensive masterclasses
- Formats luxury Dark Cyber layouts & generates 1200x630 hero PNG artwork
- Schedules social media distribution (LinkedIn & X)
- Builds and deploys live updates to Cloudflare Edge (heliatech.online)
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.helia_autonomous_director import HeliaAutonomousDirector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Helia-24/7-Daemon] %(message)s"
)
logger = logging.getLogger("Helia-Daemon")


def main():
    parser = argparse.ArgumentParser(description="Helia 24/7 Autonomous Growth Daemon")
    parser.add_argument("--interval-hours", type=float, default=4.0, help="Interval between autonomous cycles in hours (default: 4.0)")
    parser.add_argument("--once", action="store_true", help="Run a single autonomous cycle and exit")
    parser.add_argument("--no-push", action="store_true", help="Disable automatic git push to GitHub/Cloudflare")
    args = parser.parse_args()

    director = HeliaAutonomousDirector()
    auto_push = not args.no_push
    interval_seconds = int(args.interval_hours * 3600)

    print("=" * 70)
    print("🏛️ HELIA AUTONOMOUS EXECUTIVE DIRECTOR — VERSION 4.0 (100% UNATTENDED)")
    print("Mission: Scale heliatech.online to 100,000 monthly visitors & maximize affiliate MRR.")
    print(f"Cycle Interval: Every {args.interval_hours} hours | Auto-Deploy: {auto_push}")
    print("=" * 70)

    cycle_count = 1
    while True:
        cycle_start = datetime.now()
        logger.info(f"🚀 Starting Autonomous Growth Cycle #{cycle_count} at {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            director.execute_autonomous_growth_cycle(auto_push=auto_push)
            logger.info(f"✅ Autonomous Growth Cycle #{cycle_count} completed successfully!")
        except Exception as e:
            logger.error(f"❌ Error during Growth Cycle #{cycle_count}: {e}", exc_info=True)

        if args.once:
            logger.info("Executed single cycle (--once flag passed). Exiting.")
            break

        cycle_count += 1
        logger.info(f"⏳ Sleeping for {args.interval_hours} hours until next autonomous cycle... (Press Ctrl+C to stop)")
        try:
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Helia Autonomous Daemon safely terminated by user.")
            break


if __name__ == "__main__":
    main()
