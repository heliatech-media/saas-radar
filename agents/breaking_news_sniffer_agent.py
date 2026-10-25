"""
Agent: Breaking News & Changelog Sniffer (Senior Tech Trend Scout).
Continuously monitors changelogs, RSS feeds, and developer release notes of
HeliaTech's monetized partner software (ElevenLabs, Make, Supabase, Cursor, HeyGen, etc.).
Detects breaking version launches and produces high-authority "Newsjacking" teardowns
that capture search traffic within hours of official announcements.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from agents.config import GEMINI_API_KEY, GEMINI_MODEL, BLOG_CONTENT_DIR
from google import genai

RADAR_REPORT_PATH = ROOT_DIR / "reports" / "breaking_news_radar.json"

# Key RSS & Changelog feeds of high-converting partner tools
PARTNER_FEEDS = [
    {
        "partner": "Supabase",
        "tool_slug": "supabase",
        "feed_url": "https://supabase.com/blog/rss.xml",
        "keywords": ["launch", "release", "postgres", "ai", "vector", "auth", "storage", "performance"]
    },
    {
        "partner": "Make",
        "tool_slug": "make",
        "feed_url": "https://www.make.com/en/blog/rss.xml",
        "keywords": ["ai", "automation", "enterprise", "integration", "update", "new"]
    },
    {
        "partner": "OpenAI / Voice Tech",
        "tool_slug": "elevenlabs",
        "feed_url": "https://openai.com/news/rss.xml",
        "keywords": ["voice", "audio", "realtime", "api", "model", "latency", "speech"]
    }
]


class BreakingNewsSnifferAgent:
    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def fetch_feed_items(self, feed_url: str, max_items: int = 5) -> List[Dict]:
        """Fetches and parses an RSS/Atom XML feed."""
        items = []
        try:
            req = urllib.request.Request(
                feed_url,
                headers={"User-Agent": "HeliaTech-NewsSniffer/2.0 (Tech Media Benchmark Engine)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw_xml = resp.read()
                root = ET.fromstring(raw_xml)

                # Search RSS <item> tags
                channel_items = root.findall(".//item")
                if not channel_items:
                    # Check Atom <entry> tags
                    channel_items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

                for it in channel_items[:max_items]:
                    title_elem = it.find("title")
                    if title_elem is None:
                        title_elem = it.find("{http://www.w3.org/2005/Atom}title")

                    link_elem = it.find("link")
                    if link_elem is None:
                        link_elem = it.find("{http://www.w3.org/2005/Atom}link")

                    pub_elem = it.find("pubDate")
                    if pub_elem is None:
                        pub_elem = it.find("{http://www.w3.org/2005/Atom}published")
                    if pub_elem is None:
                        pub_elem = it.find("{http://www.w3.org/2005/Atom}updated")

                    desc_elem = it.find("description")
                    if desc_elem is None:
                        desc_elem = it.find("{http://www.w3.org/2005/Atom}summary")

                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled Update"
                    link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                    if not link and link_elem is not None and "href" in link_elem.attrib:
                        link = link_elem.attrib["href"]

                    pub_date = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""
                    desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""

                    # Clean HTML tags from description
                    clean_desc = re.sub(r"<[^>]+>", " ", desc)[:300].strip()

                    items.append({
                        "title": title,
                        "link": link,
                        "pub_date": pub_date,
                        "summary": clean_desc
                    })
        except Exception as e:
            # Feeds can fail gracefully without blocking the daemon
            pass
        return items

    def sniff_all_partners(self) -> Dict:
        """Scans all monitored partner feeds and identifies high-impact breaking updates."""
        sniffed_events = []

        # Load existing radar ledger
        existing_ledger = {}
        if RADAR_REPORT_PATH.exists():
            try:
                existing_ledger = json.loads(RADAR_REPORT_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass

        tracked_urls = set(existing_ledger.get("processed_urls", []))

        for target in PARTNER_FEEDS:
            partner = target["partner"]
            tool_slug = target["tool_slug"]
            items = self.fetch_feed_items(target["feed_url"])

            for it in items:
                link = it.get("link", "")
                title = it.get("title", "")
                if not link or link in tracked_urls:
                    continue

                # Check relevance to keywords
                relevance_score = 0
                title_lower = title.lower()
                for kw in target["keywords"]:
                    if kw in title_lower:
                        relevance_score += 1

                is_breaking = relevance_score >= 1 or any(hot in title_lower for hot in ["v2", "v3", "v4", "launch", "release", "benchmark"])

                sniffed_events.append({
                    "partner": partner,
                    "tool_slug": tool_slug,
                    "title": title,
                    "link": link,
                    "pub_date": it.get("pub_date", ""),
                    "summary": it.get("summary", ""),
                    "is_breaking": is_breaking,
                    "relevance_score": relevance_score
                })
                tracked_urls.add(link)

        # Update radar report
        report_data = {
            "last_scan": datetime.now().isoformat(),
            "total_events_detected": len(sniffed_events),
            "breaking_opportunities": [e for e in sniffed_events if e["is_breaking"]],
            "processed_urls": list(tracked_urls)[-100:]  # keep last 100
        }
        RADAR_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RADAR_REPORT_PATH.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return report_data


if __name__ == "__main__":
    sniffer = BreakingNewsSnifferAgent()
    print("🛰️ Sniffing partner changelogs and breaking developer feeds...")
    res = sniffer.sniff_all_partners()
    print(f"✅ Sniff complete. {res['total_events_detected']} new events detected | {len(res['breaking_opportunities'])} breaking opportunities identified.")
