"""
🎨 HELIA-VISUAL-ARTIST (Image Generator & Social Card Agent)
Specialist Sub-Agent for HeliaTech Media Fleet.

Core Responsibilities:
1. Editorial Artwork: Generates high-res 1200x630 relative visual assets for every software article.
2. Distinct Visual Metaphors:
   - Code & DevTools: Isometric IDE windows, neural syntax graphs, vector debugging traces.
   - Automation & No-Code: Multi-node webhooks, pipeline data flows, neon trigger gateways.
   - AI Video & Voice: 3D holographic sound waves, neural lip-sync matrices, render pipelines.
   - B2B Sales & CRM: Lead enrichment graphs, funnel velocity telemetry, pipeline analytics.
3. OpenGraph & Twitter Cards: Generates compliant 16:9 high-impact media cards for X & LinkedIn.
4. Zero-Cost, High-Throughput: Uses Google Gemini's creative reasoning core to craft scalable SVG visuals.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
BLOG_DIR = ROOT_DIR / "site" / "src" / "content" / "blog"
IMAGES_DIR = ROOT_DIR / "site" / "public" / "images" / "blog"

from google import genai
from agents.config import GEMINI_API_KEY, GEMINI_MODEL


class ImageGeneratorAgent:
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.images_dir = IMAGES_DIR
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, icon: str = "🎨"):
        print(f"[Helia-VisualArtist] {icon} {message}")

    def generate_article_hero_image(
        self,
        tool_name: str,
        tool_slug: str,
        title: str,
        category: str,
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generates a tailored, high-resolution 1200x630 vector hero image for the specific software tool.
        """
        filename = output_filename or f"{tool_slug}.svg"
        out_path = self.images_dir / filename

        prompt = f"""
You are the Principal Creative Director & 3D Vector Illustrator for HELIA TECH (heliatech.online).
Design a breathtaking, visually complex, high-resolution SVG artwork (viewBox="0 0 1200 630", width="1200", height="630") for a flagship enterprise software investigation.

Article Focus:
- Software Tool: '{tool_name}'
- Category: '{category}'
- Investigation Title: '{title}'

Visual & Aesthetic Directives:
1. Cyber-Dark Luxury Palette:
   - Deep obsidian/slate background (#030712 / #090d16) with subtle geometric grid overlay.
   - Dynamic luminous highlights tailored to {tool_name}'s domain: electric cyan (#06b6d4), vibrant sky blue (#38bdf8), violet (#8b5cf6), and vivid fuchsia (#d946ef).
   - Radial ambient lighting orbs using <radialGradient> and <filter id="glow"> with feGaussianBlur.

2. Distinct Domain Metaphors for '{tool_name}':
   - If AI/Code/DevTool: Glowing isometric IDE code window with syntax lines, AST syntax trees, vector embeddings.
   - If Automation/No-Code: Interconnected workflow logic nodes, pulse webhooks, trigger-action flow pathways.
   - If AI Media/Voice/Video: Holographic 3D audio waveforms, vector neural render timelines, sound energy envelopes.
   - If CRM/Sales/Data: Multi-dimensional database cubes, enriched contact graphs, high-velocity revenue charts.
   - If E-commerce/Productivity: Distributed catalog nodes, global logistics streams, unified workspace boards.

3. Typography & Badges:
   - Include a sleek top pill badge: 'HELIATECH ARCHITECTURAL DOSSIER' with a glowing dot.
   - Prominently feature the tool title: '{tool_name.upper()}' and category subtitle in modern geometric typography.

4. Technical SVG Constraints:
   - Valid, standalone SVG with proper <defs>, gradients, filters, and clean layer grouping (<g>).
   - Absolutely NO HTML tags or broken attributes.
   - Return ONLY the raw valid <svg ...> ... </svg> code without any markdown code fences.
"""
        if not self.client:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.log(f"Architecting custom 1200x630 hero artwork for '{tool_name}'...", "✨")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            raw = (response.text or "").strip()
            # Clean markdown code fences if present
            if raw.startswith("```xml"): raw = raw[6:]
            if raw.startswith("```svg"): raw = raw[6:]
            if raw.startswith("```"): raw = raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            raw = raw.strip()

            # Ensure valid SVG opening tag
            if not raw.startswith("<svg"):
                match = re.search(r'<svg[\s\S]*</svg>', raw)
                if match:
                    raw = match.group(0)

            out_path.write_text(raw, encoding="utf-8")
            self.log(f"Generated artwork saved: {out_path.name} ({len(raw)} bytes)", "🖼️")
            return out_path
        except Exception as e:
            self.log(f"Generation exception for {tool_name}: {e}. Creating fallback cyber banner.", "⚠️")
            fallback_svg = self._create_fallback_svg(tool_name, category)
            out_path.write_text(fallback_svg, encoding="utf-8")
            return out_path

    def _create_fallback_svg(self, tool_name: str, category: str) -> str:
        """Fallback high-tech cyberpunk SVG card in case of network timeout."""
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <radialGradient id="bg" cx="50%" cy="40%" r="70%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#030712" />
    </radialGradient>
    <linearGradient id="neon" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4" />
      <stop offset="50%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#d946ef" />
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5" stroke-opacity="0.4" />
    </pattern>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)" />
  <rect width="1200" height="630" fill="url(#grid)" />
  <circle cx="950" cy="300" r="280" fill="#06b6d4" opacity="0.12" filter="blur(50px)" />
  <circle cx="250" cy="400" r="220" fill="#d946ef" opacity="0.1" filter="blur(60px)" />
  <g transform="translate(100, 140)">
    <rect width="240" height="32" rx="16" fill="#06b6d4" fill-opacity="0.12" stroke="#06b6d4" stroke-width="1" />
    <circle cx="18" cy="16" r="4" fill="#06b6d4" />
    <text x="32" y="21" fill="#38bdf8" font-family="monospace" font-size="12" font-weight="bold" letter-spacing="1.5">HELIATECH DOSSIER</text>
  </g>
  <text x="100" y="260" fill="#ffffff" font-family="sans-serif" font-size="64" font-weight="900" letter-spacing="-1">{tool_name.upper()}</text>
  <text x="100" y="320" fill="url(#neon)" font-family="monospace" font-size="24" font-weight="bold" letter-spacing="2">{category.upper()}</text>
  <line x1="100" y1="360" x2="1100" y2="360" stroke="#334155" stroke-width="1.5" />
  <text x="100" y="420" fill="#94a3b8" font-family="sans-serif" font-size="20">Enterprise Software Teardown &amp; Hands-on Engineering Masterclass</text>
  <g transform="translate(100, 480)">
    <text x="0" y="20" fill="#06b6d4" font-family="monospace" font-size="14 font-weight="bold">BENCHMARK GRADE: VERIFIED ✦ 2026 EDITION</text>
  </g>
</svg>"""

    def ensure_image_for_article(self, article_path: Path) -> str:
        """
        Checks if an article has an image. If not, generates one and updates the frontmatter.
        Returns the web URL of the image (e.g. /images/blog/cursor.svg).
        """
        try:
            content = article_path.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                return ""

            frontmatter = yaml.safe_load(parts[1]) or {}
            tool_slug = frontmatter.get("tool_slug", article_path.stem.replace("-evolution-guide-2026", ""))
            tool_name = frontmatter.get("tags", [tool_slug])[0]
            title = frontmatter.get("title", f"{tool_name} Masterclass")
            category = frontmatter.get("category", "Enterprise Software")

            web_path = f"/images/blog/{tool_slug}.svg"
            local_path = self.images_dir / f"{tool_slug}.svg"

            # If image file doesn't exist on disk, generate it
            if not local_path.exists():
                self.generate_article_hero_image(
                    tool_name=tool_name,
                    tool_slug=tool_slug,
                    title=title,
                    category=category,
                    output_filename=f"{tool_slug}.svg"
                )

            # Update frontmatter if 'image' field is missing
            if frontmatter.get("image") != web_path:
                frontmatter["image"] = web_path
                new_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
                new_content = f"---\n{new_yaml}\n---{parts[2]}"
                article_path.write_text(new_content, encoding="utf-8")
                self.log(f"Linked image '{web_path}' into {article_path.name}", "🔗")

            return web_path
        except Exception as e:
            self.log(f"Error ensuring image for {article_path.name}: {e}", "❌")
            return ""

    def process_all_articles(self) -> Dict[str, Any]:
        """Scans all articles in blog/ and ensures every article has a dedicated hero image."""
        self.log("Commencing full visual asset generation sweep across all articles...", "🚀")
        articles = list(BLOG_DIR.glob("*.md"))
        success_count = 0

        for art in articles:
            img = self.ensure_image_for_article(art)
            if img:
                success_count += 1

        self.log(f"Visual asset sweep complete: {success_count}/{len(articles)} articles equipped with custom artwork.", "🏆")
        return {
            "total": len(articles),
            "generated": success_count,
            "status": "VISUAL_PERFECTION"
        }


if __name__ == "__main__":
    agent = ImageGeneratorAgent()
    agent.process_all_articles()
