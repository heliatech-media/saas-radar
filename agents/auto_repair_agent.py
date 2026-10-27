"""
🔧 Agent Auto-Repair & Log Watcher (Helia Self-Healing Core).
- Inspects Markdown and Frontmatter for YAML errors, unescaped characters, or missing fields.
- Automatically repairs malformed files in-place before build.
- Analyzes Astro compilation errors and applies instant remediation.
"""

from pathlib import Path
import yaml
import re

ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT_DIR / "site"
REVIEWS_DIR = SITE_DIR / "src" / "content" / "reviews"
BLOG_DIR = SITE_DIR / "src" / "content" / "blog"


class AutoRepairAgent:
    def __init__(self):
        self.reviews_dir = REVIEWS_DIR
        self.blog_dir = BLOG_DIR

    def scan_and_repair_content(self) -> dict:
        """Inspects all markdown content files and automatically fixes syntax issues."""
        repaired_count = 0
        inspected_count = 0
        issues = []

        all_md_files = list(self.reviews_dir.glob("*.md")) + list(self.blog_dir.glob("*.md"))

        for file in all_md_files:
            inspected_count += 1
            try:
                raw_text = file.read_text(encoding="utf-8")
                parts = raw_text.split("---")
                if len(parts) < 3:
                    issues.append(f"{file.name}: Invalid frontmatter delimiters.")
                    continue

                yaml_raw = parts[1]
                body = "---".join(parts[2:])

                # Check if YAML parses cleanly
                needs_save = False
                try:
                    data = yaml.safe_load(yaml_raw)
                except yaml.YAMLError:
                    # Sanitize unescaped characters in YAML
                    sanitized_yaml = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', yaml_raw)
                    data = yaml.safe_load(sanitized_yaml)
                    yaml_raw = yaml.dump(data, allow_unicode=True, sort_keys=False)
                    needs_save = True

                # Clean control characters in markdown body
                cleaned_body = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', body)
                if cleaned_body != body:
                    body = cleaned_body
                    needs_save = True

                if needs_save:
                    fixed_content = f"---{yaml_raw}---{body}"
                    file.write_text(fixed_content, encoding="utf-8")
                    repaired_count += 1

            except Exception as e:
                issues.append(f"{file.name}: Failed repair attempt: {e}")

        # Sync Cloudflare edge redirects
        self.sync_cloudflare_redirects()

        return {
            "inspected": inspected_count,
            "repaired": repaired_count,
            "issues": issues,
            "status": "HEALTHY" if len(issues) == 0 else "WARNING"
        }

    def sync_cloudflare_redirects(self):
        """Generates Cloudflare Pages _redirects file for instant edge 302 hops."""
        redirects_file = SITE_DIR / "public" / "_redirects"
        lines = [
            "# Strict Permanent HTTPS & Apex Domain Enforcement (Cloudflare Pages)\n",
            "http://heliatech.online/* https://heliatech.online/:splat 301!\n",
            "http://www.heliatech.online/* https://heliatech.online/:splat 301!\n",
            "https://www.heliatech.online/* https://heliatech.online/:splat 301!\n\n",
            "# Cloudflare Pages Edge Directives - Instant Affiliate Hops\n"
        ]
        for md_file in sorted(self.reviews_dir.glob("*.md")):
            slug = md_file.stem
            try:
                raw_text = md_file.read_text(encoding="utf-8")
                parts = raw_text.split("---")
                if len(parts) >= 3:
                    data = yaml.safe_load(parts[1])
                    target = data.get("affiliate_url") or data.get("website_url")
                    if target:
                        lines.append(f"/go/{slug} {target} 302\n")
            except Exception:
                continue
        redirects_file.parent.mkdir(parents=True, exist_ok=True)
        redirects_file.write_text("".join(lines), encoding="utf-8")


if __name__ == "__main__":
    agent = AutoRepairAgent()
    res = agent.scan_and_repair_content()
    print(f"[AUTO-REPAIR AGENT] Inspected: {res['inspected']} | Repaired: {res['repaired']} | Status: {res['status']}")
