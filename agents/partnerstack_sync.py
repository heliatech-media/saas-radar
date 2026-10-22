"""
Helia-Sync: Autonomous PartnerStack API Integration.
Automatically pulls referral links from PartnerStack and syncs them into HeliaTech.
"""

import os
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

PARTNERSTACK_API_KEY = os.getenv("PARTNERSTACK_API_KEY", "")
PARTNERSTACK_PARTNER_KEY = os.getenv("PARTNERSTACK_PARTNER_KEY", "")
CONFIG_PATH = ROOT_DIR / "agents" / "config.py"
DATA_INDEX_PATH = ROOT_DIR / "site" / "src" / "data" / "tools-index.json"
REVIEWS_DIR = ROOT_DIR / "site" / "src" / "content" / "reviews"


class PartnerStackSync:
    BASE_URL = "https://api.partnerstack.com/api/v2"

    def __init__(self, api_key: str = PARTNERSTACK_API_KEY, partner_key: str = PARTNERSTACK_PARTNER_KEY):
        self.api_key = api_key
        self.partner_key = partner_key
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }

    def is_configured(self) -> bool:
        return bool(self.api_key and self.partner_key)

    def fetch_active_links(self) -> dict:
        """
        Fetches all active referral links for the partner from PartnerStack.
        Returns a dict: { 'tool_slug': 'https://try.tool.io/ref' }
        """
        if not self.is_configured():
            print("[Helia-Sync] ⚠️ PARTNERSTACK_API_KEY or PARTNERSTACK_PARTNER_KEY not set.")
            return {}

        url = f"{self.BASE_URL}/links/partnership/{self.partner_key}"
        try:
            res = requests.get(url, headers=self.headers, timeout=15)
            if res.status_code != 200:
                print(f"[Helia-Sync] ❌ Error from PartnerStack API ({res.status_code}): {res.text}")
                return {}

            data = res.json()
            links_map = {}
            items = data.get("data", []) or data.get("items", []) or []

            for item in items:
                program_name = item.get("company_name") or item.get("program_name") or item.get("title", "")
                link_url = item.get("url") or item.get("target_url") or item.get("link", "")
                if program_name and link_url:
                    slug = re.sub(r'[^a-z0-9]+', '-', program_name.lower()).strip('-')
                    links_map[slug] = link_url
                    print(f"[Helia-Sync] 🔗 Found active link for '{program_name}' -> {link_url}")

            return links_map

        except Exception as e:
            print(f"[Helia-Sync] ❌ Exception connecting to PartnerStack: {e}")
            return {}

    def sync_into_heliatech(self) -> int:
        """
        Synchronizes all discovered links into AFFILIATE_MAP, reviews markdown, and index.
        """
        links = self.fetch_active_links()
        if not links:
            return 0

        # 1. Update config.py
        if CONFIG_PATH.exists():
            content = CONFIG_PATH.read_text(encoding="utf-8")
            # Replace AFFILIATE_MAP content
            map_repr = json.dumps(links, indent=4)
            new_content = re.sub(
                r'AFFILIATE_MAP\s*=\s*\{[^}]*\}',
                f'AFFILIATE_MAP = {map_repr}',
                content
            )
            CONFIG_PATH.write_text(new_content, encoding="utf-8")
            print(f"[Helia-Sync] ✅ Updated AFFILIATE_MAP in {CONFIG_PATH}")

        # 2. Update reviews markdown files
        for slug, url in links.items():
            md_file = REVIEWS_DIR / f"{slug}.md"
            if md_file.exists():
                text = md_file.read_text(encoding="utf-8")
                updated_text = re.sub(r'affiliate_url:\s*.*', f'affiliate_url: {url}', text)
                md_file.write_text(updated_text, encoding="utf-8")
                print(f"[Helia-Sync] ✅ Updated review frontmatter: {md_file.name}")

        # 3. Update tools-index.json
        if DATA_INDEX_PATH.exists():
            try:
                tools = json.loads(DATA_INDEX_PATH.read_text(encoding="utf-8"))
                for tool in tools:
                    t_slug = tool.get("slug")
                    if t_slug in links:
                        tool["affiliate_url"] = links[t_slug]
                DATA_INDEX_PATH.write_text(json.dumps(tools, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[Helia-Sync] ✅ Synchronized search index data.")
            except Exception as e:
                print(f"[Helia-Sync] ⚠️ Could not update index JSON: {e}")

        return len(links)


if __name__ == "__main__":
    syncer = PartnerStackSync()
    count = syncer.sync_into_heliatech()
    print(f"[Helia-Sync] 🚀 Synchronization complete. {count} links processed.")
