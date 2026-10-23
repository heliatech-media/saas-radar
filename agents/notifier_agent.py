"""
Helia-Notifier: Autonomous Real-Time Alerting Engine for the Founder.
Delivers instant, rich push notifications to Telegram and Discord
whenever high-yield milestones, new monetization deals, or publications occur.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import requests
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-Notifier] %(message)s")
logger = logging.getLogger("Helia-Notifier")

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

NOTIFICATIONS_LOG_PATH = ROOT_DIR / "reports" / "live_notifications.json"


class NotifierAgent:
    """
    Real-time push notifier across Telegram & Discord.
    """
    def __init__(self):
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

    def is_configured(self) -> bool:
        return bool((self.telegram_bot_token and self.telegram_chat_id) or self.discord_webhook_url)

    def send_notification(self, title: str, message: str, category: str = "INFO", link: Optional[str] = None) -> bool:
        """
        Broadcasts an executive alert to active channels (Telegram, Discord, Local Inbox).
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_text = f"🏛️ **[HELIA NOTIFICATION]** {title}\n📅 {timestamp}\n\n{message}"
        if link:
            formatted_text += f"\n🔗 {link}"

        sent_anywhere = False

        # 1. Telegram Push
        if self.telegram_bot_token and self.telegram_chat_id:
            try:
                tg_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                payload = {
                    "chat_id": self.telegram_chat_id,
                    "text": formatted_text,
                    "parse_mode": "Markdown"
                }
                res = requests.post(tg_url, json=payload, timeout=8)
                if res.status_code == 200:
                    logger.info("✅ Telegram alert successfully delivered to founder.")
                    sent_anywhere = True
                else:
                    logger.warning(f"Telegram API response: {res.text}")
            except Exception as e:
                logger.error(f"Error sending Telegram notification: {e}")

        # 2. Discord Webhook Push
        if self.discord_webhook_url:
            try:
                discord_payload = {
                    "username": "Helia Autonomous Director",
                    "avatar_url": "https://heliatech.online/images/social/linkedin-avatar.png",
                    "embeds": [{
                        "title": title,
                        "description": message,
                        "url": link or "https://heliatech.online/sentinel/suivicontrol",
                        "color": 0x06b6d4 if category == "INFO" else 0x10b981,
                        "footer": {"text": f"Helia Sentinel • {timestamp}"}
                    }]
                }
                res = requests.post(self.discord_webhook_url, json=discord_payload, timeout=8)
                if res.status_code in (200, 204):
                    logger.info("✅ Discord webhook alert successfully delivered.")
                    sent_anywhere = True
            except Exception as e:
                logger.error(f"Error sending Discord notification: {e}")

        # 3. Always log to local persistent notifications feed
        try:
            NOTIFICATIONS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            notifications = []
            if NOTIFICATIONS_LOG_PATH.exists():
                try:
                    notifications = json.loads(NOTIFICATIONS_LOG_PATH.read_text(encoding="utf-8"))
                except Exception:
                    notifications = []

            notifications.insert(0, {
                "timestamp": timestamp,
                "title": title,
                "category": category,
                "message": message,
                "link": link
            })
            # Keep last 50
            notifications = notifications[:50]
            NOTIFICATIONS_LOG_PATH.write_text(json.dumps(notifications, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Error persisting local notification: {e}")

        if not self.is_configured():
            logger.info(f"Notification recorded locally: '{title}' (Configure TELEGRAM_BOT_TOKEN or DISCORD_WEBHOOK_URL for mobile alerts).")

        return sent_anywhere

    def notify_monetization(self, tool_name: str, commission: str, hop_url: str):
        title = f"💰 NOUVEL OUTIL MONÉTISÉ : {tool_name.upper()}"
        msg = f"L'agent Helia-AffiliateHunter a activé la monétisation pour {tool_name} !\n• Taux de commission : {commission}\n• Redirection Edge active : {hop_url}"
        return self.send_notification(title, msg, category="MONEY", link=hop_url)

    def notify_publication(self, article_title: str, url: str):
        title = f"📰 NOUVELLE MASTERCLASS PUBLIÉE"
        msg = f"Helia vient de compiler et déployer un nouvel article d'autorité en direct sur le web :\n« {article_title} »"
        return self.send_notification(title, msg, category="CONTENT", link=url)


if __name__ == "__main__":
    notifier = NotifierAgent()
    print("\n--- Helia-Notifier Status ---")
    print(f"Telegram Configured: {bool(notifier.telegram_bot_token and notifier.telegram_chat_id)}")
    print(f"Discord Configured: {bool(notifier.discord_webhook_url)}")
    print("\nTesting local dispatch...")
    notifier.send_notification(
        title="Système Autonome 4.0 Actif",
        message="Helia-Notifier est opérationnel et prêt à relayer les alertes stratégiques.",
        category="INFO",
        link="https://heliatech.online/sentinel/suivicontrol"
    )
    print("Test concluded successfully.")
