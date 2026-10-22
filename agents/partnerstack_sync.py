"""
Helia-Sync: Autonomous PartnerStack API Integration.
Automatically pulls all active partnerships and referral links from PartnerStack
and injects them directly into HeliaTech.
"""

import os
import sys
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

PARTNERSTACK_API_KEY = os.getenv("PARTNERSTACK_API_KEY", "")
CONFIG_PATH = ROOT_DIR / "agents" / "config.py"
DATA_INDEX_PATH = ROOT_DIR / "site" / "src" / "data" / "tools-index.json"
REVIEWS_DIR = ROOT_DIR / "site" / "src" / "content" / "reviews"


class PartnerStackSync:
    ENDPOINT = "https://api.partnerstack.com/api/v2/partnerships"

    def __init__(self, api_key: str = PARTNERSTACK_API_KEY):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def fetch_active_links(self) -> dict:
        """
        Queries PartnerStack v2 partnerships API.
        Extracts { 'slug': 'affiliate_link' } for all active partner programs.
        """
        if not self.is_configured():
            print("[Helia-Sync] ⚠️ PARTNERSTACK_API_KEY not configured.")
            return {}

        try:
            res = requests.get(self.ENDPOINT, headers=self.headers, timeout=15)
            if res.status_code != 200:
                print(f"[Helia-Sync] ❌ PartnerStack API Error ({res.status_code}): {res.text}")
                return {}

            payload = res.json()
            data = payload.get("data", {})
            items = data.get("items", []) if isinstance(data, dict) else []

            links_map = {}
            for item in items:
                status = item.get("status", "")
                if status != "active":
                    continue

                company = item.get("company", {})
                company_name = company.get("name", "")
                link_obj = item.get("link", {})
                link_url = link_obj.get("url", "")

                if company_name and link_url:
                    # Clean company name into slug (e.g. 'Eleven Labs Inc.' -> 'elevenlabs')
                    clean_name = re.sub(r'\b(inc|corp|llc|co|ai)\b', '', company_name, flags=re.IGNORECASE)
                    slug = re.sub(r'[^a-z0-9]+', '', clean_name.lower())
                    
                    # Common normalizations
                    if "eleven" in slug:
                        slug = "elevenlabs"
                    elif "monday" in slug:
                        slug = "monday-com"
                    elif "webflow" in slug:
                        slug = "webflow"
                    elif "brevo" in slug or "sendinblue" in slug:
                        slug = "brevo"
                    elif "lusha" in slug:
                        slug = "lusha"

                    links_map[slug] = link_url
                    print(f"[Helia-Sync] [LINK] Active partnership: '{company_name}' -> {link_url} (slug: {slug})")

            return links_map

        except Exception as e:
            print(f"[Helia-Sync] [ERROR] Exception during PartnerStack sync: {e}")
            return {}

    def sync_into_heliatech(self) -> int:
        """
        Synchronizes all discovered links into AFFILIATE_MAP, reviews markdown, and index.
        """
        links = self.fetch_active_links()
        if not links:
            return 0

        # 1. Update agents/config.py (MERGE with existing affiliate map)
        if CONFIG_PATH.exists():
            content = CONFIG_PATH.read_text(encoding="utf-8")
            # Extract current map if present
            current_map = {}
            match = re.search(r'AFFILIATE_MAP\s*=\s*(\{[\s\S]*?\n\})', content)
            if match:
                try:
                    # Parse as python dict literal safely
                    import ast
                    current_map = ast.literal_eval(match.group(1))
                except Exception:
                    current_map = {}
            # Merge PartnerStack links
            current_map.update(links)
            map_repr = json.dumps(current_map, indent=4)
            new_content = re.sub(
                r'AFFILIATE_MAP\s*=\s*\{[\s\S]*?\n\}',
                f'AFFILIATE_MAP = {map_repr}',
                content
            )
            CONFIG_PATH.write_text(new_content, encoding="utf-8")
            print(f"[Helia-Sync] [OK] Merged and updated AFFILIATE_MAP in {CONFIG_PATH}")

        # 2. Update reviews markdown files
        for slug, url in links.items():
            md_file = REVIEWS_DIR / f"{slug}.md"
            if md_file.exists():
                text = md_file.read_text(encoding="utf-8")
                updated_text = re.sub(r'affiliate_url:\s*.*', f'affiliate_url: {url}', text)
                md_file.write_text(updated_text, encoding="utf-8")
                print(f"[Helia-Sync] [OK] Updated review: {md_file.name}")

        # 3. Update tools-index.json
        if DATA_INDEX_PATH.exists():
            try:
                tools = json.loads(DATA_INDEX_PATH.read_text(encoding="utf-8"))
                for tool in tools:
                    t_slug = tool.get("slug")
                    if t_slug in links:
                        tool["affiliate_url"] = links[t_slug]
                DATA_INDEX_PATH.write_text(json.dumps(tools, indent=2, ensure_ascii=False), encoding="utf-8")
                print(f"[Helia-Sync] [OK] Updated search index JSON.")
            except Exception as e:
                print(f"[Helia-Sync] [WARN] Could not update index JSON: {e}")

        return len(links)


if __name__ == "__main__":
    syncer = PartnerStackSync()
    count = syncer.sync_into_heliatech()
    print(f"[Helia-Sync] [COMPLETE] Synchronization complete. {count} active links linked.")
