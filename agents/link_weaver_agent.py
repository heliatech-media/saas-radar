"""
Helia-LinkWeaver: Autonomous Semantic Internal Linking & Topical Mesh Agent.
Scans all published articles and reviews, detects contextual mentions of other
catalog tools, and injects natural internal hyperlinks.
Constructs an authoritative Google-ranked topic cluster (cocon sémantique).
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-LinkWeaver] %(message)s")
logger = logging.getLogger("Helia-LinkWeaver")

ROOT_DIR = Path(__file__).resolve().parent.parent
BLOG_DIR = ROOT_DIR / "site" / "src" / "content" / "blog"
REVIEWS_DIR = ROOT_DIR / "site" / "src" / "content" / "reviews"

# Target entities to weave throughout content
ENTITY_MAP = {
    "Make": "/reviews/make",
    "Zapier": "/reviews/zapier",
    "ElevenLabs": "/reviews/elevenlabs",
    "HeyGen": "/reviews/heygen",
    "Supabase": "/reviews/supabase",
    "Airtable": "/reviews/airtable",
    "Apollo.io": "/reviews/apollo-io",
    "Lusha": "/reviews/lusha",
    "ClickUp": "/reviews/clickup",
    "Monday.com": "/reviews/monday-com",
    "Beehiiv": "/reviews/beehiiv",
    "Brevo": "/reviews/brevo",
    "Retool": "/reviews/retool",
    "Voiceflow": "/reviews/voiceflow",
    "Webflow": "/reviews/webflow",
    "Linear": "/reviews/linear",
    "AdCreative.ai": "/reviews/adcreative-ai",
    "Cursor": "/reviews/cursor",
    "Notion AI": "/reviews/notion-ai"
}


class LinkWeaverAgent:
    """
    Autonomous Internal Linking Weaver.
    """
    def __init__(self):
        self.blog_dir = BLOG_DIR
        self.reviews_dir = REVIEWS_DIR

    def weave_file(self, file_path: Path) -> int:
        """
        Injects up to 1 contextual internal link per target entity into the markdown content.
        Safely ignores YAML frontmatter, headings, code blocks, and already linked text.
        """
        content = file_path.read_text(encoding="utf-8")
        current_slug = file_path.stem.lower()

        # Split frontmatter from body
        parts = content.split("---", 2)
        if len(parts) < 3:
            return 0

        frontmatter = parts[1]
        body = parts[2]

        links_added = 0
        
        # Protect code blocks and existing links
        # We process line by line
        lines = body.split("\n")
        in_code_block = False
        new_lines = []

        # Track entities linked in this document to avoid over-linking
        linked_entities = set()

        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                new_lines.append(line)
                continue

            if in_code_block or line.strip().startswith("#"):
                new_lines.append(line)
                continue

            # Check each entity in ENTITY_MAP
            for entity, url in ENTITY_MAP.items():
                if entity.lower() in current_slug:
                    # Do not self-link to current tool review
                    continue

                if entity in linked_entities:
                    continue

                # Pattern matching entity not already inside markdown link [Entity](...)
                # Regex matches whole word with boundary
                pattern = rf'(?<!\[)\b{re.escape(entity)}\b(?!\]|\()'
                
                if re.search(pattern, line):
                    # Replace only first occurrence on this line
                    line = re.sub(pattern, f"[{entity}]({url})", line, count=1)
                    linked_entities.add(entity)
                    links_added += 1

            new_lines.append(line)

        if links_added > 0:
            updated_body = "\n".join(new_lines)
            updated_content = f"---{frontmatter}---{updated_body}"
            file_path.write_text(updated_content, encoding="utf-8")
            logger.info(f"Weaved {links_added} internal links into {file_path.name}")

        return links_added

    def weave_all(self) -> Dict[str, int]:
        """Runs the linking sweep across all blog articles and reviews."""
        total_links = 0
        files_updated = 0

        target_files = list(self.blog_dir.glob("*.md")) + list(self.reviews_dir.glob("*.md"))
        logger.info(f"Starting semantic link weaving across {len(target_files)} content files...")

        for f in target_files:
            count = self.weave_file(f)
            if count > 0:
                total_links += count
                files_updated += 1

        logger.info(f"✨ Internal link weaving complete: {total_links} semantic connections established across {files_updated} files.")
        return {
            "total_links_added": total_links,
            "files_updated": files_updated
        }


if __name__ == "__main__":
    weaver = LinkWeaverAgent()
    res = weaver.weave_all()
    print(f"\n--- Helia-LinkWeaver Summary ---")
    print(f"Total Internal Links Injected: {res['total_links_added']}")
    print(f"Files Strengthened for Google: {res['files_updated']}")
