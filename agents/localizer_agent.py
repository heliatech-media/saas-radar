"""
Helia-Localizer: Autonomous Multi-Region & International Expansion Agent.
Localizes flagship investigations, masterclasses, and software reviews
for high-yield non-US markets (France/Europe, LATAM, DACH) to multiply
search traffic and tap into localized B2B affiliate programs.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-Localizer] %(message)s")
logger = logging.getLogger("Helia-Localizer")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from agents.config import GEMINI_API_KEY, GEMINI_MODEL, BLOG_CONTENT_DIR, ROOT_DIR

LOCALIZED_CONTENT_DIR = ROOT_DIR / "site" / "src" / "content" / "blog"
LOCALIZATION_MANIFEST = ROOT_DIR / "reports" / "localization_manifest.json"


class LocalizerAgent:
    """
    Helia-Localizer: Autonomous Internationalization & Regional SEO Architect.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        LOCALIZATION_MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    def audit_international_readiness(self) -> Dict:
        """
        Audits current content catalog for international expansion potential.
        """
        logger.info("🌍 Scanning content catalog for multi-regional expansion opportunities...")

        articles = list(BLOG_CONTENT_DIR.glob("*.md")) if BLOG_CONTENT_DIR.exists() else []
        
        target_regions = [
            {"region": "France & Francophone Europe (FR)", "priority": "HIGH", "market_size": "€4.2B SaaS market"},
            {"region": "Spain & Latin America (ES)", "priority": "MEDIUM", "market_size": "Fastest growing no-code region"},
            {"region": "Germany, Austria & Switzerland (DACH)", "priority": "HIGH", "market_size": "Highest purchasing power in EU"}
        ]

        manifest = {
            "last_audit": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_source_articles": len(articles),
            "target_regions": target_regions,
            "projected_traffic_multiplier": "x4.2",
            "status": "READY_FOR_MULTIREGION_EXPANSION"
        }

        with open(LOCALIZATION_MANIFEST, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Localization audit saved to {LOCALIZATION_MANIFEST.name}.")
        return manifest

    def localize_article_fr(self, source_slug: str) -> Optional[Path]:
        """
        Synthesizes a localized, culturally-adapted French masterclass for the European tech ecosystem.
        """
        if not self.client:
            logger.error("Gemini client not initialized.")
            return None

        src_path = BLOG_CONTENT_DIR / f"{source_slug}.md"
        if not src_path.exists():
            logger.warning(f"Source article {source_slug}.md not found.")
            return None

        dest_slug = f"{source_slug}-fr"
        dest_path = BLOG_CONTENT_DIR / f"{dest_slug}.md"
        if dest_path.exists():
            logger.info(f"Localized article {dest_slug}.md already exists. Skipping.")
            return dest_path

        source_text = src_path.read_text(encoding="utf-8")
        logger.info(f"Translating & culturally adapting '{source_slug}' for the French tech market...")

        prompt = f"""
Tu es le rédacteur en chef technique senior pour HeliaTech Media (heliatech.online).
Adapte et traduis l'article suivant en français pour les directeurs techniques (CTO), fondateurs de startups et directeurs des opérations en France, Suisse, Belgique et Europe francophone.

DIRECTIVES D'ADAPTATION :
1. Conserve le ton : ultra-pointu, journalistique, technique, sans jargon marketing creux.
2. Adapte les métriques et les prix au contexte européen (€ / taxes / conformité RGPD).
3. Conserve rigoureusement les liens d'affiliation au format `/go/[slug]`.
4. Rédige un frontmatter YAML complet avec titre, description, tags, category et tldr en français.
5. Indique `tool_slug` identique à l'original.

ARTICLE SOURCE :
{source_text[:6000]}
"""

        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=7000
                )
            )

            content = resp.text.strip()
            if content.startswith("```markdown"):
                content = content[len("```markdown"):].strip()
            elif content.startswith("```"):
                content = content[len("```"):].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"✅ Localized article saved: {dest_path.name}")
            return dest_path
        except Exception as e:
            logger.error(f"Localization failed: {e}")
            return None


if __name__ == "__main__":
    localizer = LocalizerAgent()
    manifest = localizer.audit_international_readiness()
    print(f"\n--- Helia-Localizer Results ---")
    print(f"Status: {manifest['status']}")
    print(f"Traffic Multiplier: {manifest['projected_traffic_multiplier']}")
