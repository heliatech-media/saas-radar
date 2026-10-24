"""
🎨 HELIA-ARTICLE-STYLIST (Article Layout & Visual Experience Agent)
Specialist Sub-Agent for HeliaTech Media Fleet.

Core Responsibilities:
1. Editorial Typesetting: Formats articles with drop caps, visual callout boxes, and readable hierarchy.
2. Architecture Visualization: Injects Mermaid sequence and flow diagrams into workshops.
3. Feature Comparison Matrices: Formats responsive tables with visual status glyphs (✅, ⚠️, ❌).
4. Step-by-Step Workshop Layouts: Transforms raw tutorials into numbered, digestible execution blueprints.
5. In-Content Micro-CTAs: Injects high-converting, non-intrusive transition badges linking to reviews & tools.
6. Reading Retention Optimization: Analyzes paragraph length, visual rhythm, and scannability.
"""

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
BLOG_DIR = ROOT_DIR / "site" / "src" / "content" / "blog"


class ArticleLayoutAgent:
    def __init__(self, blog_dir: Optional[Path] = None):
        self.blog_dir = blog_dir or BLOG_DIR

    def log(self, message: str, icon: str = "🎨"):
        print(f"[Helia-ArticleStylist] {icon} {message}")

    def beautify_markdown(self, markdown_body: str, tool_name: str, tool_slug: str, category: str) -> str:
        """
        Enhances raw markdown content with luxury cyber-editorial layout elements:
        - Callout cards (Pro-Tips, Warnings, ROI takeaways)
        - Mermaid workflow visualization if missing
        - Formatted step headers
        - Mid-article high-converting transition pill
        """
        lines = markdown_body.split("\n")
        formatted_lines = []
        has_mermaid = "```mermaid" in markdown_body
        in_code_block = False
        inserted_diagram = has_mermaid
        inserted_mid_cta = ("Benchmark Access:" in markdown_body or f"/go/{tool_slug}" in markdown_body)

        in_blockquote = False
        for i, line in enumerate(lines):
            # Track code block fences
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                formatted_lines.append(line)
                in_blockquote = False
                continue

            if in_code_block:
                formatted_lines.append(line)
                continue

            # 1. Handle blockquotes idempotently
            if line.startswith("> "):
                quote_text = line[2:].strip()
                # If already formatted or continuing an alert block, keep as-is
                if (
                    quote_text.startswith("[!") or
                    "executive takeaway" in quote_text.lower() or
                    "benchmark access" in quote_text.lower() or
                    "pro-tip" in quote_text.lower() or
                    "trade-off" in quote_text.lower() or
                    in_blockquote
                ):
                    formatted_lines.append(line)
                elif "pro tip" in quote_text.lower() or "tip:" in quote_text.lower():
                    clean = re.sub(r'^(pro tip:?|tip:?)\s*', '', quote_text, flags=re.IGNORECASE)
                    formatted_lines.append(f"> [!TIP]\n> **HeliaTech Pro-Tip:** {clean}")
                elif "warning" in quote_text.lower() or "caution" in quote_text.lower():
                    clean = re.sub(r'^(warning:?|caution:?)\s*', '', quote_text, flags=re.IGNORECASE)
                    formatted_lines.append(f"> [!WARNING]\n> **Critical Trade-Off:** {clean}")
                else:
                    formatted_lines.append(f"> [!NOTE]\n> **Executive Takeaway:** {quote_text}")
                in_blockquote = True
                continue
            else:
                in_blockquote = False

            # 2. Inject Mermaid workflow diagram right before Workshop section if not present
            if not inserted_diagram and re.search(r'^##\s+(3\.|.*Hands-on.*|.*Workshop.*)', line, re.IGNORECASE):
                mermaid_block = f"""
```mermaid
flowchart LR
    A[Manual Bottleneck] --> B[{tool_name} Engine]
    B --> C[Automated Workflow]
    C --> D[ROI Multiplier]
    style B fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#030712
    style D fill:#d946ef,stroke:#c026d3,stroke-width:2px,color:#ffffff
```
"""
                formatted_lines.append(mermaid_block.strip())
                formatted_lines.append("")
                inserted_diagram = True

            # 3. Enhance Step titles with visual badges (e.g., Step 1, Step 2)
            step_match = re.match(r'^(###|\*\*|\b)(Step\s+[0-9]+:?)(.*)', line, re.IGNORECASE)
            if step_match and not in_code_block and not line.startswith("### ⚡"):
                step_num = step_match.group(2).strip().rstrip(':')
                step_title = step_match.group(3).strip().lstrip(':-* ')
                formatted_lines.append(f"### ⚡ {step_num}: {step_title}")
                continue

            # 4. Inject mid-article high-converting transition pill after Section 2 (Core Superpowers)
            if not inserted_mid_cta and re.search(r'^##\s+(3\.|.*Workshop.*)', line, re.IGNORECASE):
                mid_cta = f"""
> [!TIP]
> **HeliaTech Benchmark Access:** Test `{tool_name}` with our verified enterprise trial link at [/go/{tool_slug}](/go/{tool_slug}).
"""
                formatted_lines.append(mid_cta.strip())
                formatted_lines.append("")
                inserted_mid_cta = True

            formatted_lines.append(line)

        # Return sanitized and polished markdown
        result = "\n".join(formatted_lines)
        return result

    def format_single_article(self, article_path: Path) -> bool:
        """Reads, beautifies, and writes back an article file."""
        try:
            content = article_path.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                return False

            frontmatter_raw = parts[1]
            body = parts[2]
            frontmatter = yaml.safe_load(frontmatter_raw) or {}

            tool_name = frontmatter.get("tags", [article_path.stem])[0]
            tool_slug = frontmatter.get("tool_slug", article_path.stem.replace("-evolution-guide-2026", ""))
            category = frontmatter.get("category", "B2B SaaS")

            polished_body = self.beautify_markdown(body, tool_name=tool_name, tool_slug=tool_slug, category=category)

            # Ensure readingTime is calculated accurately (~200 words/min)
            word_count = len(polished_body.split())
            mins = max(5, round(word_count / 200))
            frontmatter["readingTime"] = f"{mins} MIN"

            # Reconstruct YAML & File
            new_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
            new_content = f"---\n{new_yaml}\n---\n{polished_body.lstrip()}"

            article_path.write_text(new_content, encoding="utf-8")
            return True
        except Exception as e:
            self.log(f"Failed to format {article_path.name}: {e}", "⚠️")
            return False

    def beautify_all_articles(self) -> Dict[str, Any]:
        """Scans all articles in blog/ and enhances layout for each."""
        self.log("Commencing comprehensive layout & visual formatting sweep...", "📐")
        articles = list(self.blog_dir.glob("*.md"))
        success_count = 0

        for art in articles:
            if self.format_single_article(art):
                success_count += 1

        self.log(f"Completed formatting for {success_count}/{len(articles)} articles.", "✨")
        return {
            "total_articles": len(articles),
            "formatted_count": success_count,
            "status": "LAYOUT_PERFECTED"
        }


if __name__ == "__main__":
    agent = ArticleLayoutAgent()
    agent.beautify_all_articles()
