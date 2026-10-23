"""
Helia-AffiliateHub: Unified Multi-Network Autonomous Affiliate API Connector.
Enables HeliaTech agents to programmatically query affiliate networks (Impact.com,
PartnerStack, CJ Affiliate, Rewardful), auto-generate dedicated tracking links,
and synchronize edge redirects and editorial reviews without human intervention.
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

# Ensure UTF-8 console output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-AffiliateHub] %(message)s")
logger = logging.getLogger("Helia-AffiliateHub")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
load_dotenv(ROOT_DIR / ".env")

CONFIG_PATH = ROOT_DIR / "agents" / "config.py"
DATA_INDEX_PATH = ROOT_DIR / "site" / "src" / "data" / "tools-index.json"
REVIEWS_DIR = ROOT_DIR / "site" / "src" / "content" / "reviews"
REDIRECTS_PATH = ROOT_DIR / "site" / "public" / "_redirects"

# Known canonical slug normalizations
SLUG_NORMALIZATIONS = {
    "eleven": "elevenlabs",
    "elevenlabs": "elevenlabs",
    "make": "make",
    "integromat": "make",
    "clickup": "clickup",
    "adcreative": "adcreative-ai",
    "brevo": "brevo",
    "sendinblue": "brevo",
    "monday": "monday-com",
    "mondaycom": "monday-com",
    "airtable": "airtable",
    "apollo": "apollo-io",
    "apolloio": "apollo-io",
    "heygen": "heygen",
    "lusha": "lusha",
    "notion": "notion-ai",
    "n8n": "n8n",
    "partnerstack": "partnerstack",
    "printify": "printify",
    "retool": "retool",
    "voiceflow": "voiceflow",
    "wati": "wati",
    "webflow": "webflow",
    "zapier": "zapier",
    "beehiiv": "beehiiv",
    "cursor": "cursor",
    "surfer": "surfer-seo",
    "semrush": "semrush",
    "canva": "canva",
    "hubspot": "hubspot"
}


def normalize_to_slug(raw_name: str) -> str:
    """Normalize company/campaign name to a canonical HeliaTech tool slug."""
    clean = re.sub(r'\b(inc|corp|llc|ltd|co|ai|io|com|app|software|technologies|the)\b', '', raw_name, flags=re.IGNORECASE)
    clean = re.sub(r'[^a-z0-9]+', '', clean.lower()).strip()
    
    for key, slug in SLUG_NORMALIZATIONS.items():
        if key in clean:
            return slug
    return clean


class BaseNetworkAdapter:
    """Abstract adapter for an affiliate network API."""
    name: str = "base"

    def is_configured(self) -> bool:
        raise NotImplementedError

    def fetch_links(self) -> Dict[str, str]:
        """Returns dict of { slug: affiliate_tracking_url }"""
        raise NotImplementedError


class ImpactAdapter(BaseNetworkAdapter):
    """
    Impact.com (Impact Radius) Publisher REST API Adapter.
    Endpoint: https://api.impact.com/Mediapartners/{AccountSID}/Campaigns
    Documentation: https://developer.impact.com/mediapartner/
    """
    name = "Impact.com"

    def __init__(self):
        self.account_sid = os.getenv("IMPACT_ACCOUNT_SID", "").strip()
        self.auth_token = os.getenv("IMPACT_AUTH_TOKEN", "").strip()
        self.base_url = f"https://api.impact.com/Mediapartners/{self.account_sid}" if self.account_sid else ""

    def is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token)

    def fetch_links(self) -> Dict[str, str]:
        if not self.is_configured():
            logger.info("Impact.com adapter not configured (IMPACT_ACCOUNT_SID missing).")
            return {}

        results = {}
        try:
            url = f"{self.base_url}/Campaigns"
            auth = (self.account_sid, self.auth_token)
            headers = {"Accept": "application/json"}
            
            logger.info("Querying Impact.com campaigns API...")
            res = requests.get(url, auth=auth, headers=headers, timeout=15)
            
            if res.status_code != 200:
                logger.error(f"Impact.com API returned HTTP {res.status_code}: {res.text[:200]}")
                return {}

            data = res.json()
            campaigns = data.get("Campaigns", [])
            for camp in campaigns:
                state = camp.get("State", "")
                if state.lower() not in ("active", "joined"):
                    continue

                campaign_name = camp.get("CampaignName", "")
                campaign_id = camp.get("CampaignId", "")
                slug = normalize_to_slug(campaign_name)

                # Fetch or generate tracking link
                link_url = camp.get("DefaultLandingPageUrl", "")
                tracking_endpoint = f"{self.base_url}/Campaigns/{campaign_id}/TrackingLinks"
                t_res = requests.get(tracking_endpoint, auth=auth, headers=headers, timeout=10)
                if t_res.status_code == 200:
                    t_data = t_res.json()
                    links = t_data.get("TrackingLinks", [])
                    if links:
                        link_url = links[0].get("TrackingURL", link_url)

                if slug and link_url:
                    # Append sub-id tracking for Helia analytics
                    delim = "&" if "?" in link_url else "?"
                    if "subId1=" not in link_url:
                        link_url = f"{link_url}{delim}subId1=heliatech"
                    results[slug] = link_url
                    logger.info(f"[Impact.com] Linked '{campaign_name}' -> {link_url} (slug: {slug})")

        except Exception as e:
            logger.error(f"Error querying Impact.com API: {e}")

        return results


class PartnerStackAdapter(BaseNetworkAdapter):
    """
    PartnerStack Partner REST API Adapter.
    Endpoint: https://api.partnerstack.com/api/v2/partnerships
    """
    name = "PartnerStack"

    def __init__(self):
        self.api_key = os.getenv("PARTNERSTACK_API_KEY", "").strip()
        self.endpoint = "https://api.partnerstack.com/api/v2/partnerships"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def fetch_links(self) -> Dict[str, str]:
        if not self.is_configured():
            logger.info("PartnerStack adapter not configured (PARTNERSTACK_API_KEY missing).")
            return {}

        results = {}
        try:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            logger.info("Querying PartnerStack partnerships API...")
            res = requests.get(self.endpoint, headers=headers, timeout=15)
            if res.status_code != 200:
                logger.error(f"PartnerStack API returned HTTP {res.status_code}: {res.text[:200]}")
                return {}

            payload = res.json()
            data = payload.get("data", {})
            items = data.get("items", []) if isinstance(data, dict) else []

            for item in items:
                if item.get("status", "") != "active":
                    continue
                company_name = item.get("company", {}).get("name", "")
                link_url = item.get("link", {}).get("url", "")
                if company_name and link_url:
                    slug = normalize_to_slug(company_name)
                    results[slug] = link_url
                    logger.info(f"[PartnerStack] Linked '{company_name}' -> {link_url} (slug: {slug})")

        except Exception as e:
            logger.error(f"Error querying PartnerStack API: {e}")

        return results


class CJAdapter(BaseNetworkAdapter):
    """
    CJ Affiliate (Commission Junction) REST / GraphQL Link API Adapter.
    Endpoint: https://commissions.api.cj.com/graphql
    """
    name = "CJ Affiliate"

    def __init__(self):
        self.token = os.getenv("CJ_PERSONAL_ACCESS_TOKEN", "").strip()
        self.company_id = os.getenv("CJ_COMPANY_ID", "").strip()
        self.endpoint = "https://commissions.api.cj.com/graphql"

    def is_configured(self) -> bool:
        return bool(self.token and self.company_id)

    def fetch_links(self) -> Dict[str, str]:
        if not self.is_configured():
            logger.info("CJ Affiliate adapter not configured (CJ_PERSONAL_ACCESS_TOKEN missing).")
            return {}

        results = {}
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            # GraphQL query to retrieve active advertiser links
            query = """
            query {
                publisher(companyId: "%s") {
                    joinedAdvertisers {
                        advertiserId
                        advertiserName
                        programTerms {
                            defaultLink {
                                clickUrl
                            }
                        }
                    }
                }
            }
            """ % self.company_id

            logger.info("Querying CJ Affiliate GraphQL API...")
            res = requests.post(self.endpoint, headers=headers, json={"query": query}, timeout=15)
            if res.status_code == 200:
                data = res.json()
                advertisers = data.get("data", {}).get("publisher", {}).get("joinedAdvertisers", [])
                for adv in advertisers:
                    name = adv.get("advertiserName", "")
                    link = adv.get("programTerms", {}).get("defaultLink", {}).get("clickUrl", "")
                    if name and link:
                        slug = normalize_to_slug(name)
                        results[slug] = link
                        logger.info(f"[CJ Affiliate] Linked '{name}' -> {link} (slug: {slug})")
            else:
                logger.error(f"CJ API Error ({res.status_code}): {res.text[:200]}")

        except Exception as e:
            logger.error(f"Error querying CJ Affiliate API: {e}")

        return results


class HeliaAffiliateHub:
    """
    Central Orchestrator for Multi-Network Affiliate API Management.
    """
    def __init__(self):
        self.adapters: List[BaseNetworkAdapter] = [
            ImpactAdapter(),
            PartnerStackAdapter(),
            CJAdapter()
        ]

    def list_supported_adapters(self) -> List[Dict]:
        return [
            {
                "network": adapter.name,
                "configured": adapter.is_configured()
            }
            for adapter in self.adapters
        ]

    def pull_all_links(self) -> Dict[str, str]:
        """Queries all configured network adapters and returns consolidated dictionary."""
        consolidated = {}
        for adapter in self.adapters:
            if adapter.is_configured():
                links = adapter.fetch_links()
                consolidated.update(links)
        return consolidated

    def sync_into_system(self, discovered_links: Optional[Dict[str, str]] = None) -> Dict:
        """
        Merges discovered links into:
        1. agents/config.py (AFFILIATE_MAP)
        2. site/src/content/reviews/*.md
        3. site/src/data/tools-index.json
        4. site/public/_redirects (Cloudflare edge hops)
        """
        if discovered_links is None:
            discovered_links = self.pull_all_links()

        if not discovered_links:
            logger.info("No active API links retrieved from networks.")
            return {"synced_count": 0, "tools": []}

        # 1. Update agents/config.py
        if CONFIG_PATH.exists():
            content = CONFIG_PATH.read_text(encoding="utf-8")
            current_map = {}
            match = re.search(r'AFFILIATE_MAP\s*=\s*(\{[\s\S]*?\n\})', content)
            if match:
                try:
                    import ast
                    current_map = ast.literal_eval(match.group(1))
                except Exception:
                    current_map = {}
            
            # Merge
            current_map.update(discovered_links)
            map_repr = json.dumps(current_map, indent=4)
            new_content = re.sub(
                r'AFFILIATE_MAP\s*=\s*\{[\s\S]*?\n\}',
                f'AFFILIATE_MAP = {map_repr}',
                content
            )
            CONFIG_PATH.write_text(new_content, encoding="utf-8")
            logger.info("Updated AFFILIATE_MAP in agents/config.py.")

        # 2. Update reviews markdown files
        for slug, url in discovered_links.items():
            md_file = REVIEWS_DIR / f"{slug}.md"
            if md_file.exists():
                text = md_file.read_text(encoding="utf-8")
                updated_text = re.sub(r'affiliate_url:\s*.*', f'affiliate_url: {url}', text)
                md_file.write_text(updated_text, encoding="utf-8")
                logger.info(f"Updated review frontmatter: {md_file.name}")

        # 3. Update tools-index.json
        if DATA_INDEX_PATH.exists():
            try:
                tools = json.loads(DATA_INDEX_PATH.read_text(encoding="utf-8"))
                for tool in tools:
                    t_slug = tool.get("slug")
                    if t_slug in discovered_links:
                        tool["affiliate_url"] = discovered_links[t_slug]
                DATA_INDEX_PATH.write_text(json.dumps(tools, indent=2, ensure_ascii=False), encoding="utf-8")
                logger.info("Updated tools-index.json search index.")
            except Exception as e:
                logger.warning(f"Could not update tools-index.json: {e}")

        # 4. Regenerate site/public/_redirects
        from scripts.update_redirects import generate
        generate()
        logger.info("Regenerated site/public/_redirects with latest affiliate endpoints.")

        return {
            "synced_count": len(discovered_links),
            "tools": list(discovered_links.keys())
        }


if __name__ == "__main__":
    hub = HeliaAffiliateHub()
    status = hub.list_supported_adapters()
    print("\n--- Helia-AffiliateHub Status ---")
    for s in status:
        state = "✅ Configured" if s["configured"] else "⚪ Awaiting API credentials"
        print(f" • {s['network']}: {state}")
    
    print("\nRunning test synchronization...")
    res = hub.sync_into_system()
    print(f"Result: {res['synced_count']} tools synchronized.\n")
