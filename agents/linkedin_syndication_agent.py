"""
LinkedIn Syndication & Authority Distribution Engine for HeliaTech Media.
Publishes high-converting 'Standard Emblème' technical breakdowns directly to LinkedIn
via its official REST API v2, with rich OpenGraph media cards and verified affiliate redirects.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import requests
import yaml

# Load environment & paths
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from agents.config import BLOG_CONTENT_DIR, AFFILIATE_MAP, GEMINI_API_KEY, GEMINI_MODEL
from agents.models import BlogPost, AffiliateCTA
from agents.social_growth_agent import SocialGrowthAgent

LEDGER_PATH = ROOT_DIR / "reports" / "linkedin_syndication_ledger.json"
LINKEDIN_API_URL = "https://api.linkedin.com/v2/ugcPosts"


def load_ledger() -> dict:
    if LEDGER_PATH.exists():
        try:
            return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"published_posts": {}, "last_publish": None}


def save_ledger(data: dict):
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_frontmatter(content: str) -> tuple[dict, str]:
    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_fm = parts[1]
            body = parts[2].strip()
            try:
                parsed = yaml.safe_load(raw_fm)
                if isinstance(parsed, dict):
                    frontmatter = parsed
            except Exception as e:
                print(f"[LinkedIn Syndicator] Warning: Failed to parse YAML frontmatter: {e}")

    return frontmatter, body


def get_monetized_queue() -> list[str]:
    """Returns only articles that have active, verified affiliate monetization."""
    monetized_slugs = []

    # Priority queue: high-converting B2B software
    priority_order = [
        "eleven-v4-voice-ai-benchmark",
        "make-vs-zapier",
        "apollo-io-vs-lusha",
        "submagic-evolution-guide-2026",
        "adcreative-ai-evolution-guide-2026",
        "beehiiv-evolution-guide-2026",
        "transistor-evolution-guide-2026",
        "clickup-vs-monday-com",
        "supabase-vs-retool",
        "heygen-evolution-guide-2026"
    ]

    available_slugs = set()
    for md_file in BLOG_CONTENT_DIR.glob("*.md"):
        slug = md_file.stem
        try:
            content = md_file.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
            tool_slug = fm.get("tool_slug", "")
            
            is_monetized = False
            if tool_slug and tool_slug in AFFILIATE_MAP:
                is_monetized = True
            else:
                for k in AFFILIATE_MAP.keys():
                    if k in slug:
                        is_monetized = True
                        break

            if is_monetized:
                available_slugs.add(slug)
        except Exception:
            continue

    # Order priority items first, then others
    for p in priority_order:
        if p in available_slugs:
            monetized_slugs.append(p)

    for s in sorted(available_slugs):
        if s not in monetized_slugs:
            monetized_slugs.append(s)

    return monetized_slugs


class LinkedInSyndicator:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()

        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.author_urn = os.getenv("LINKEDIN_AUTHOR_URN", "")
        self.broadcast_enabled = os.getenv("LINKEDIN_BROADCAST_ENABLED", "false").lower() == "true"
        self.social_agent = SocialGrowthAgent()

    def syndicate_next_article(self, force_slug: str = None) -> dict:
        """Publishes the next monetized article from the queue to LinkedIn."""
        if not self.broadcast_enabled:
            print("[LinkedIn Syndicator] 🔒 LINKEDIN_BROADCAST_ENABLED is not 'true'. Broadcast aborted.")
            return {"status": "STANDBY", "reason": "broadcast_disabled"}

        if not self.access_token or not self.author_urn:
            print("[LinkedIn Syndicator] ❌ Missing LINKEDIN_ACCESS_TOKEN or LINKEDIN_AUTHOR_URN in .env.")
            return {"status": "ERROR", "reason": "missing_credentials"}

        ledger = load_ledger()
        published = set(ledger.get("published_posts", {}).keys())

        target_slug = force_slug
        if not target_slug:
            queue = get_monetized_queue()
            remaining = [s for s in queue if s not in published]
            if not remaining:
                print("[LinkedIn Syndicator] ℹ️ All monetized articles have already been published to LinkedIn!")
                return {"status": "COMPLETE", "message": "all_articles_published"}
            target_slug = remaining[0]

        md_path = BLOG_CONTENT_DIR / f"{target_slug}.md"
        if not md_path.exists():
            print(f"[LinkedIn Syndicator] ❌ Article file not found: {md_path}")
            return {"status": "ERROR", "reason": "file_not_found"}

        content = md_path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(content)

        tool_slug = fm.get("tool_slug", target_slug.replace("-evolution-guide-2026", ""))
        title = fm.get("title", f"{tool_slug.capitalize()} Enterprise Audit")
        desc = fm.get("description", "")
        cat = fm.get("category", "SaaS")
        tldr = fm.get("tldr", [])

        post = BlogPost(
            title=title,
            slug=target_slug,
            description=desc,
            date=str(fm.get("date", datetime.now().date())),
            author=fm.get("author", "Helia Tech"),
            category=cat,
            tags=fm.get("tags", [tool_slug]),
            image=f"/images/blog/{tool_slug}.svg",
            readingTime=fm.get("readingTime", "7 MIN"),
            tool_slug=tool_slug,
            tldr=tldr if isinstance(tldr, list) else [str(tldr)],
            affiliate_cta=AffiliateCTA(
                badge="OFFICIAL HELIATECH PARTNERSHIP",
                title=f"Access {tool_slug.capitalize()}",
                description="Explore enterprise capabilities.",
                button_text="Get Started",
                url=f"/go/{tool_slug}"
            ),
            markdown_content=body
        )

        print(f"[LinkedIn Syndicator] ✍️ Crafting Standard Emblème LinkedIn breakdown for '{tool_slug}'...")
        linkedin_text = self.social_agent.craft_linkedin_authority_post(post)

        canonical_url = f"https://heliatech.online/blog/{target_slug}"
        png_url = f"https://heliatech.online/images/blog/{tool_slug}.png"

        # Construct LinkedIn ugcPosts Payload
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        media_item = {
            "status": "READY",
            "originalUrl": canonical_url,
            "title": {"text": title[:200]}
        }
        if png_url:
            media_item["thumbnails"] = [{"url": png_url}]

        payload = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": linkedin_text
                    },
                    "shareMediaCategory": "ARTICLE",
                    "media": [media_item]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        try:
            res = requests.post(LINKEDIN_API_URL, json=payload, headers=headers, timeout=20)
            if res.status_code in [200, 201]:
                data = res.json()
                share_urn = data.get("id")
                print(f"[LinkedIn Syndicator] ✅ SUCCESS! Published post to LinkedIn for '{target_slug}'")
                print(f"                       Share URN: {share_urn}")

                # Record in ledger
                ledger["published_posts"][target_slug] = {
                    "published_at": datetime.now().isoformat(),
                    "share_urn": share_urn,
                    "title": title,
                    "tool_slug": tool_slug,
                    "canonical_url": canonical_url
                }
                ledger["last_publish"] = datetime.now().isoformat()
                save_ledger(ledger)

                return {
                    "status": "SUCCESS",
                    "slug": target_slug,
                    "share_urn": share_urn,
                    "canonical_url": canonical_url
                }
            else:
                print(f"[LinkedIn Syndicator] ⚠️ Error broadcasting to LinkedIn: {res.status_code} - {res.text}")
                return {"status": "API_ERROR", "code": res.status_code, "detail": res.text}
        except Exception as e:
            print(f"[LinkedIn Syndicator] ❌ Exception during LinkedIn broadcast: {e}")
            return {"status": "EXCEPTION", "error": str(e)}


if __name__ == "__main__":
    syndicator = LinkedInSyndicator()
    force = sys.argv[1] if len(sys.argv) > 1 else None
    result = syndicator.syndicate_next_article(force_slug=force)
    print(f"\nResult: {json.dumps(result, indent=2)}")
