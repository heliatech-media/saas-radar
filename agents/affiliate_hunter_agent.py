"""
Helia-AffiliateHunter: Autonomous Software Partner & Affiliate Link Discovery Agent.
Empowered with 100% executive autonomy by Helia-Core.
Scans unmonetized software in the HeliaTech catalog, analyzes their official partner
programs, discovers referral parameters/portals, and auto-monetizes them into edge redirects.
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-AffiliateHunter] %(message)s")
logger = logging.getLogger("Helia-AffiliateHunter")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from agents.config import GEMINI_API_KEY, GEMINI_MODEL, CONTENT_DIR, DATA_DIR, AGENTS_DIR
from scripts.update_redirects import generate as update_edge_redirects

CONFIG_PATH = AGENTS_DIR / "config.py"
REVIEWS_DIR = CONTENT_DIR
DATA_INDEX_PATH = DATA_DIR / "tools-index.json"


class AffiliateHunterAgent:
    """
    Autonomous Affiliate Link & Partner Program Discovery Engine.
    Executes independently without human intervention.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def scan_unmonetized_tools(self) -> List[Dict[str, str]]:
        """
        Scans site/src/content/reviews/*.md to identify tools that still lack an affiliate link
        (i.e., where affiliate_url is empty or points to the root homepage without tracking parameters).
        """
        unmonetized = []
        if not REVIEWS_DIR.exists():
            return unmonetized

        for md_file in sorted(REVIEWS_DIR.glob("*.md")):
            slug = md_file.stem
            content = md_file.read_text(encoding="utf-8")
            
            aff_url = ""
            web_url = ""
            name = slug.replace("-", " ").title()

            for line in content.splitlines():
                if line.startswith("title:"):
                    name = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("affiliate_url:"):
                    aff_url = line.split(":", 1)[1].strip().strip('"\'')
                elif line.startswith("website_url:"):
                    web_url = line.split(":", 1)[1].strip().strip('"\'')

            # Tool is unmonetized if affiliate_url is empty, or identical to plain website_url without query params
            is_unmonetized = (
                not aff_url or
                aff_url == web_url or
                ("?" not in aff_url and "/" not in aff_url.replace("https://", "").replace("http://", "").rstrip("/"))
            )

            # Keep known manual active affiliate links untouched
            if slug in ("elevenlabs", "make"):
                is_unmonetized = False

            if is_unmonetized:
                unmonetized.append({
                    "slug": slug,
                    "name": name,
                    "website_url": web_url or f"https://www.{slug}.com",
                    "file_path": str(md_file)
                })

        logger.info(f"Found {len(unmonetized)} unmonetized software assets ready for autonomous affiliate hunting.")
        return unmonetized

    def hunt_affiliate_program(self, tool_info: Dict[str, str]) -> Optional[Dict]:
        """
        Uses Gemini to investigate the software's affiliate ecosystem,
        detecting whether it uses PartnerStack, Rewardful, FirstPromoter, Impact, or direct query parameters.
        """
        if not self.client:
            logger.warning("Gemini API client not initialized. Cannot perform AI affiliate hunting.")
            return None

        prompt = f"""
You are Helia-AffiliateHunter, Chief Monetization Scout for HeliaTech Media (heliatech.online).
Perform deep research on the official affiliate or partner program of:
- Software Name: "{tool_info['name']}"
- Slug: "{tool_info['slug']}"
- Official Website: "{tool_info['website_url']}"

Analyze and determine:
1. Which affiliate platform manages their program (e.g., "PartnerStack", "Rewardful", "FirstPromoter", "Impact", "ShareASale", "CJ", or "In-House Referral").
2. The exact public affiliate signup URL or partner portal page (e.g. "https://[tool].com/partners", "https://[tool].rewardful.com", "https://app.impact.com/...").
3. What is their canonical referral link format?
   - Many tools accept a publisher referral tag (e.g. "?via=heliatech", "?ref=heliatech", "?fpr=heliatech", or custom partner tracking).
4. Commission structure (e.g. "30% recurring", "20% per sale", "$50 CPA").
5. The best optimized tracking link for HeliaTech Media (our brand identifier is "heliatech" or "heliatechmake").

Output strictly valid JSON with this exact schema:
{{
  "platform": "string (Rewardful | PartnerStack | Impact | FirstPromoter | In-House)",
  "partner_portal_url": "string (URL to their partner/affiliate info page)",
  "commission_rate": "string (e.g. '30% recurring')",
  "cookie_window_days": 60,
  "canonical_affiliate_url": "string (e.g. 'https://tool.com/?via=heliatech' or partner tracking link)"
}}
"""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            raw = response.text.strip()
            data = json.loads(raw)
            return data
        except Exception as e:
            logger.error(f"Error researching affiliate program for {tool_info['name']}: {e}")
            return None

    def monetize_tool(self, tool_info: Dict[str, str], intelligence: Dict) -> bool:
        """
        Applies the discovered affiliate tracking link to HeliaTech:
        - Updates agents/config.py (AFFILIATE_MAP)
        - Updates site/src/content/reviews/[slug].md
        - Updates site/src/data/tools-index.json
        """
        slug = tool_info["slug"]
        aff_url = intelligence.get("canonical_affiliate_url", "").strip()

        if not aff_url or not aff_url.startswith("http"):
            logger.warning(f"Invalid affiliate URL returned for {slug}: {aff_url}")
            return False

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
            current_map[slug] = aff_url
            map_repr = json.dumps(current_map, indent=4)
            new_content = re.sub(
                r'AFFILIATE_MAP\s*=\s*\{[\s\S]*?\n\}',
                f'AFFILIATE_MAP = {map_repr}',
                content
            )
            CONFIG_PATH.write_text(new_content, encoding="utf-8")
            logger.info(f"Updated AFFILIATE_MAP with {slug} -> {aff_url}")

        # 2. Update reviews markdown file
        md_path = Path(tool_info["file_path"])
        if md_path.exists():
            text = md_path.read_text(encoding="utf-8")
            text = re.sub(r'affiliate_url:\s*.*', f'affiliate_url: "{aff_url}"', text)
            md_path.write_text(text, encoding="utf-8")
            logger.info(f"Updated {md_path.name} with new affiliate URL.")

        # 3. Update tools-index.json
        if DATA_INDEX_PATH.exists():
            try:
                tools = json.loads(DATA_INDEX_PATH.read_text(encoding="utf-8"))
                for t in tools:
                    if t.get("slug") == slug:
                        t["affiliate_url"] = aff_url
                        t["commission_rate"] = intelligence.get("commission_rate", t.get("commission_rate", "30%"))
                DATA_INDEX_PATH.write_text(json.dumps(tools, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception as e:
                logger.warning(f"Error updating tools-index.json: {e}")

        return True

    def execute_hunt_cycle(self, max_tools: int = 3) -> Dict:
        """
        Full autonomous hunt cycle:
        1. Find unmonetized tools in catalog
        2. Research their affiliate programs
        3. Inject discovered links
        4. Regenerate Cloudflare edge redirects
        """
        logger.info(f"Executing autonomous affiliate hunt cycle (Limit: {max_tools} tools)...")
        unmonetized = self.scan_unmonetized_tools()
        if not unmonetized:
            logger.info("All tools in the catalog are already monetized!")
            return {"hunted": 0, "tools": []}

        hunted_tools = []
        for tool in unmonetized[:max_tools]:
            logger.info(f"Hunting affiliate intelligence for '{tool['name']}'...")
            intel = self.hunt_affiliate_program(tool)
            if intel and intel.get("canonical_affiliate_url"):
                success = self.monetize_tool(tool, intel)
                if success:
                    hunted_tools.append({
                        "slug": tool["slug"],
                        "name": tool["name"],
                        "platform": intel.get("platform", "In-House"),
                        "commission": intel.get("commission_rate", "Recurring"),
                        "link": intel.get("canonical_affiliate_url")
                    })
                    logger.info(f"Successfully monetized '{tool['name']}' via {intel.get('platform')} ({intel.get('commission_rate')})!")

        if hunted_tools:
            update_edge_redirects()
            logger.info(f"Regenerated Cloudflare edge redirects for {len(hunted_tools)} newly monetized tools.")

        return {
            "hunted": len(hunted_tools),
            "tools": hunted_tools
        }


if __name__ == "__main__":
    hunter = AffiliateHunterAgent()
    res = hunter.execute_hunt_cycle(max_tools=2)
    print("\n--- Helia-AffiliateHunter Autonomous Hunt Results ---")
    print(f"Newly Monetized Tools: {res['hunted']}")
    for t in res["tools"]:
        print(f" • {t['name']} ({t['platform']}) -> {t['link']} | Rate: {t['commission']}")
