"""
DEV.to Syndication Agent for HeliaTech Media.
Automatically syndicates high-authority blog articles to DEV.to via its official API,
setting canonical URLs back to heliatech.online to drive traffic and boost Google SEO.
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
import urllib.request
import urllib.error

# Load environment & paths
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from agents.config import DEVTO_API_KEY, BLOG_CONTENT_DIR

LEDGER_PATH = ROOT_DIR / "reports" / "devto_syndication_ledger.json"
DEVTO_API_URL = "https://dev.to/api/articles"


def load_ledger() -> dict:
    if LEDGER_PATH.exists():
        try:
            return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"syndicated_articles": {}, "last_sync": None}


def save_ledger(data: dict):
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


import yaml

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown content."""
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
                print(f"Warning: Failed to parse YAML frontmatter: {e}")

    return frontmatter, body


def get_monetized_queue() -> list[str]:
    """Returns a list of blog slugs that have active monetization in AFFILIATE_MAP."""
    from agents.config import AFFILIATE_MAP
    monetized_slugs = []

    for md_file in BLOG_CONTENT_DIR.glob("*.md"):
        slug = md_file.stem
        try:
            content = md_file.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
            tool_slug = fm.get("tool_slug", "")
            # If tool_slug matches a key in AFFILIATE_MAP or slug contains an affiliate partner name
            is_monetized = False
            if tool_slug and tool_slug in AFFILIATE_MAP:
                is_monetized = True
            else:
                for k in AFFILIATE_MAP.keys():
                    if k in slug:
                        is_monetized = True
                        break

            if is_monetized:
                monetized_slugs.append(slug)
        except Exception:
            continue

    return sorted(monetized_slugs)


def syndicate_next_monetized_article() -> dict:
    """Finds and syndicates the next available monetized blog article not yet published to DEV.to."""
    ledger = load_ledger()
    already_published = set(ledger.get("syndicated_articles", {}).keys())
    queue = get_monetized_queue()

    remaining = [slug for slug in queue if slug not in already_published]

    if not remaining:
        print("[DEV.to Syndicator] All monetized articles have already been syndicated!")
        return {"status": "complete", "message": "Queue exhausted"}

    next_slug = remaining[0]
    print(f"[DEV.to Syndicator] Next candidate for publication: {next_slug} ({len(remaining)} remaining)")
    res = publish_article(next_slug, publish_live=True)
    return {"status": "syndicated", "slug": next_slug, "result": res}
    """DEV.to allows up to 4 tags, alphanumeric lowercase only."""
    clean = []
    default_tags = ["ai", "saas", "webdev", "productivity"]
    tag_aliases = {
        "elevenv4": "ai",
        "voiceai": "audio",
        "texttospeech": "machinelearning",
        "elevenlabs": "technology"
    }
    
    for t in raw_tags:
        cleaned = re.sub(r"[^a-zA-Z0-9]", "", t).lower()
        if cleaned in tag_aliases:
            cleaned = tag_aliases[cleaned]
        if cleaned and cleaned not in clean:
            clean.append(cleaned)
        if len(clean) >= 4:
            break

    for dt in default_tags:
        if len(clean) >= 4:
            break
        if dt not in clean:
            clean.append(dt)

    return clean[:4]


def publish_article(
    slug: str,
    publish_live: bool = True,
    dry_run: bool = False
) -> dict:
    api_key = DEVTO_API_KEY or os.getenv("DEVTO_API_KEY", "")
    if not api_key and not dry_run:
        raise ValueError("DEVTO_API_KEY is missing from environment or agents/config.py")

    md_file = BLOG_CONTENT_DIR / f"{slug}.md"
    if not md_file.exists():
        # Try finding file without extension
        matches = list(BLOG_CONTENT_DIR.glob(f"*{slug}*.md"))
        if matches:
            md_file = matches[0]
            slug = md_file.stem
        else:
            raise FileNotFoundError(f"Article file not found for slug: {slug}")

    raw_text = md_file.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(raw_text)

    title = fm.get("title", slug.replace("-", " ").title())
    description = fm.get("description", title)
    canonical_url = f"https://heliatech.online/blog/{slug}"
    main_image = f"https://heliatech.online/images/blog/{slug}.png"

    # Tags formatting
    raw_tags = []
    if "tags" in fm:
        raw_val = fm["tags"]
        if isinstance(raw_val, list):
            raw_tags = [str(t) for t in raw_val]
        elif isinstance(raw_val, str):
            raw_tags = [t.strip() for t in raw_val.split(",") if t.strip()]
    if not raw_tags:
        raw_tags = ["ai", "saas", "tech"]
    tags = sanitize_tags(raw_tags)

    # Format body with canonical backlink footer
    canonical_footer = (
        f"\n\n---\n"
        f"*Originally benchmarked and published on [HeliaTech Media]({canonical_url}) — "
        f"Independent SaaS & Cloud Architecture Intelligence.*"
    )
    full_markdown = body + canonical_footer

    payload = {
        "article": {
            "title": title,
            "published": publish_live,
            "body_markdown": full_markdown,
            "main_image": main_image,
            "canonical_url": canonical_url,
            "description": description,
            "tags": tags
        }
    }

    if dry_run:
        print("[DRY-RUN] Article payload prepared:")
        print(f"  Title: {title}")
        print(f"  Canonical URL: {canonical_url}")
        print(f"  Image: {main_image}")
        print(f"  Tags: {tags}")
        print(f"  Published: {publish_live}")
        return {"status": "dry_run", "slug": slug, "title": title}

    req = urllib.request.Request(
        DEVTO_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "HeliaTech-Agent/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            devto_url = resp_data.get("url", "")
            devto_id = resp_data.get("id")

            ledger = load_ledger()
            ledger["syndicated_articles"][slug] = {
                "id": devto_id,
                "url": devto_url,
                "title": title,
                "canonical_url": canonical_url,
                "published": publish_live,
                "tags": tags
            }
            save_ledger(ledger)

            print(f" Successfully syndicated to DEV.to!")
            print(f"  URL: {devto_url}")
            print(f"  ID: {devto_id}")
            print(f"  Canonical Backlink: {canonical_url}")
            return resp_data

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"[ERROR] HTTP Error {e.code}: {error_body}")
        if e.code == 429:
            print("[INFO] DEV.to rate limit hit (max ~1 article per 30-60s on new accounts). Please wait a minute before publishing next article.")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Syndicate articles to DEV.to")
    parser.add_argument("--slug", type=str, default="eleven-v4-voice-ai-benchmark", help="Article slug to publish")
    parser.add_argument("--draft", action="store_true", help="Publish as draft instead of live")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making API call")

    args = parser.parse_args()
    publish_article(slug=args.slug, publish_live=not args.draft, dry_run=args.dry_run)
