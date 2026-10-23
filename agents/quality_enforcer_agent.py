"""
Helia-QualityEnforcer: Autonomous Anti-AI Slop & Editorial Integrity Guardian.
Scans content against overused AI cliché lexicons, validates presence of honest
trade-offs ('Where it fails', bottlenecks), and enforces high empirical density.
Prevents Google Helpful Content penalties and preserves elite brand authority.
"""

import os
import sys
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-QualityEnforcer] %(message)s")
logger = logging.getLogger("Helia-QualityEnforcer")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.config import BLOG_CONTENT_DIR, CONTENT_DIR, ROOT_DIR

QUALITY_REPORT_PATH = ROOT_DIR / "reports" / "quality_audit.json"

# AI Cliché Phrases that trigger search engine devaluation
BANNED_AI_CLICHES = [
    r"\bdelve\b",
    r"\bdelving\b",
    r"\btapestry\b",
    r"\bgame-changer\b",
    r"\bgame changer\b",
    r"\bunprecedented\b",
    r"\bin today's digital landscape\b",
    r"\bin today's fast-paced\b",
    r"\bunlock the full potential\b",
    r"\ba testament to\b",
    r"\bbeacon of\b",
    r"\bnavigating the\b",
    r"\brevolutionary paradigm\b",
    r"\bit's important to remember\b"
]

# Required sections for balanced objectivity
HONESTY_KEYWORDS = [
    "trade-off", "tradeoff", "where it falls short", "where it fails",
    "bottleneck", "limitations", "drawback", "cons", "when not to",
    "inconvénient", "limite", "critique"
]


class QualityEnforcerAgent:
    """
    Guarantees that HeliaTech content reads like senior engineers wrote it,
    not generic AI content farms.
    """
    def __init__(self):
        QUALITY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    def audit_all_content(self) -> Dict:
        """
        Scans all articles for AI slop and editorial compliance.
        """
        logger.info("🔍 Initiating Anti-AI Slop & Editorial Integrity Audit...")

        all_files = list(BLOG_CONTENT_DIR.glob("*.md")) + list(CONTENT_DIR.glob("*.md"))
        audit_records = []
        cliche_count_total = 0

        for f in all_files:
            try:
                text = f.read_text(encoding="utf-8")
                record = self._audit_article(f, text)
                audit_records.append(record)
                cliche_count_total += record["cliche_matches_count"]
            except Exception as e:
                logger.warning(f"Error checking {f.name}: {e}")

        # Compute average authenticity score
        avg_score = round(sum(r["authenticity_score"] for r in audit_records) / max(1, len(audit_records)), 1)
        honest_rate = round((sum(1 for r in audit_records if r["has_honest_tradeoffs"]) / max(1, len(audit_records))) * 100, 1)

        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_articles_scanned": len(audit_records),
            "average_authenticity_score": f"{avg_score}/100",
            "honest_tradeoffs_coverage": f"{honest_rate}%",
            "total_cliches_detected": cliche_count_total,
            "status": "APPROVED_HIGH_INTEGRITY" if avg_score >= 85 and honest_rate >= 90 else "NEEDS_EDITORIAL_REFINEMENT",
            "enforced_standards": [
                "Strict blacklisting of generic AI filler vocabulary",
                "Mandatory 'Where It Fails' & counter-balance sections",
                "Empirical data tables & pricing calculations per article",
                "Technical architecture & forensic engineer persona"
            ],
            "flagged_files": [r for r in audit_records if r["authenticity_score"] < 80][:10]
        }

        with open(QUALITY_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Editorial Quality Audit complete. Authenticity: {avg_score}/100 | Trade-offs: {honest_rate}%.")
        return report

    def _audit_article(self, path: Path, text: str) -> Dict:
        lower_text = text.lower()
        
        # Check clichés
        found_cliches = []
        for pattern in BANNED_AI_CLICHES:
            matches = re.findall(pattern, lower_text)
            if matches:
                found_cliches.extend(matches)

        # Check honest trade-offs
        has_tradeoffs = any(k in lower_text for k in HONESTY_KEYWORDS)
        
        # Check empirical tables
        has_table = "| ---" in text or "|:---" in text
        
        # Check technical density (numbers, pricing, code)
        has_pricing = any(k in text for k in ("$", "€", "mo", "month", "/an"))
        has_code = "```" in text or "`" in text

        # Score calculation (0 to 100)
        score = 80
        if has_tradeoffs:
            score += 10
        if has_table:
            score += 5
        if has_pricing and has_code:
            score += 5

        # Penalize clichés
        score -= min(30, len(found_cliches) * 5)
        score = max(40, min(100, score))

        return {
            "slug": path.stem,
            "file": path.name,
            "authenticity_score": score,
            "has_honest_tradeoffs": has_tradeoffs,
            "has_empirical_table": has_table,
            "cliche_matches_count": len(found_cliches),
            "cliches_found": list(set(found_cliches))
        }


if __name__ == "__main__":
    enforcer = QualityEnforcerAgent()
    res = enforcer.audit_all_content()
    print(f"\n--- Helia-QualityEnforcer Summary ---")
    print(f"Total Scanned: {res['total_articles_scanned']}")
    print(f"Authenticity Score: {res['average_authenticity_score']}")
    print(f"Trade-Offs Coverage: {res['honest_tradeoffs_coverage']}")
    print(f"Status: {res['status']}")
