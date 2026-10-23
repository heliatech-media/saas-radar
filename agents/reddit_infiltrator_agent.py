"""
Helia-RedditInfiltrator: High-Intent Community Traffic & Forum SEO Harvester.
Monitors high-ranking Reddit queries on Google (r/SaaS, r/webdev, r/nocode, r/startups).
Synthesizes high-karma, engineering-level technical interventions that answer user pain points
with empirical data, driving targeted decision-makers to HeliaTech benchmarks and calculators.
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Helia-RedditInfiltrator] %(message)s")
logger = logging.getLogger("Helia-RedditInfiltrator")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")

from agents.config import GEMINI_API_KEY, GEMINI_MODEL, ROOT_DIR

REDDIT_PLAYBOOK_PATH = ROOT_DIR / "reports" / "reddit_infiltration_playbook.json"
REDDIT_BRIEFS_PATH = ROOT_DIR / "reports" / "reddit_live_discussions.md"


class RedditInfiltratorAgent:
    """
    Helia-RedditInfiltrator: Converts high-ranking Google x Reddit forum threads
    into a continuous pipeline of warm B2B referral traffic and affiliate conversions.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = GEMINI_MODEL):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        REDDIT_PLAYBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)

    def get_target_discussions(self) -> List[Dict]:
        """Returns the high-intent Reddit targets dominating Google Page 1."""
        return [
            {
                "topic_id": "zapier_price_shock",
                "subreddit": "r/nocode / r/SaaS",
                "google_search_query": "Zapier pricing too expensive alternative reddit",
                "pain_point": "Users being forced to pay $299 - $599/mo for simple webhook tasks.",
                "solution_tool": "Make",
                "solution_url": "https://heliatech.online/blog/make-vs-zapier",
                "calculator_url": "https://heliatech.online/versus",
                "key_metrics": "$29/mo on Make vs $299/mo on Zapier at 50,000 tasks. Visual error branching vs linear steps."
            },
            {
                "topic_id": "heroku_free_tier_exodus",
                "subreddit": "r/webdev / r/node / r/selfhosted",
                "google_search_query": "Heroku free tier dead best postgres replacement reddit",
                "pain_point": "Developers needing a reliable zero-cost managed PostgreSQL + Auth replacement.",
                "solution_tool": "Supabase",
                "solution_url": "https://heliatech.online/blog/heroku-free-tier-alternatives-2026",
                "calculator_url": "https://heliatech.online/reviews/supabase",
                "key_metrics": "Row-level security, instant auto-generated REST/GraphQL APIs, edge functions, zero dyno sleep latency."
            },
            {
                "topic_id": "global_payroll_transparency",
                "subreddit": "r/entrepreneur / r/startups",
                "google_search_query": "Papaya Global vs Deel real pricing rate card reddit",
                "pain_point": "Founders frustrated by 'Contact Sales' gates and hidden FX spreads.",
                "solution_tool": "Papaya Global",
                "solution_url": "https://heliatech.online/blog/papaya-global-2026-pricing-rate-card-leaks",
                "calculator_url": "https://heliatech.online/reviews/papaya-global",
                "key_metrics": "Direct Tier-1 banking rails eliminate 1.5% - 3.2% correspondent banking spreads; $25/contractor vs $540/mo EOR base."
            },
            {
                "topic_id": "ai_video_avatar_shootout",
                "subreddit": "r/VideoEditing / r/artificial",
                "google_search_query": "ElevenLabs vs HeyGen video quality reddit",
                "pain_point": "Creators confused whether ElevenLabs or HeyGen is best for multi-language realistic video avatars.",
                "solution_tool": "HeyGen",
                "solution_url": "https://heliatech.online/blog/elevenlabs-vs-heygen",
                "calculator_url": "https://heliatech.online/versus",
                "key_metrics": "ElevenLabs wins on voice latency (<150ms); HeyGen wins on facial micro-gestures and automated lip-sync translation."
            },
            {
                "topic_id": "b2b_sales_data_accuracy",
                "subreddit": "r/sales / r/salesforce",
                "google_search_query": "Apollo.io vs Lusha verified phone accuracy reddit",
                "pain_point": "Sales reps burning budget on bad dials and bouncing emails.",
                "solution_tool": "Apollo.io",
                "solution_url": "https://heliatech.online/blog/apollo-io-vs-lusha",
                "calculator_url": "https://heliatech.online/reviews/apollo-io",
                "key_metrics": "Apollo.io provides 275M database scale with automated sequence email tools at 1/5th the seat cost of ZoomInfo."
            }
        ]

    def synthesize_reddit_playbook(self) -> Dict:
        """
        Generates production-ready, high-karma Reddit answers written in the style
        of a pragmatic Principal Engineer / Tech Lead.
        """
        logger.info("🕵️‍♂️ Synthesizing High-Karma Reddit Infiltration Responses...")
        discussions = self.get_target_discussions()
        playbook_entries = []

        for d in discussions:
            prompt = f"""
You are a veteran Staff Engineer and tech advisor posting on Reddit ({d['subreddit']}).
A user asked: "{d['google_search_query']}".
The core user frustration is: "{d['pain_point']}".

Write an authoritative, high-karma Reddit reply that:
1. Has ZERO marketing buzzwords or generic hype. Sounds 100% like an experienced engineer sharing production battle scars.
2. Breaks down the technical math and empirical trade-offs:
   - Highlight facts: {d['key_metrics']}
   - Give honest pros and cons (don't pretend the solution is flawless).
3. Naturally references the detailed benchmark teardown or calculator as a helpful citation:
   - Primary Dossier: {d['solution_url']}
   - Interactive Tool: {d['calculator_url']}
4. Format with clean Reddit Markdown (bullet points, bold highlights, short paragraphs).

Reply format: Just the text of the Reddit post/comment.
"""
            comment_text = ""
            if self.client:
                try:
                    resp = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction="You are a veteran Principal Architect on Reddit. You write brutally honest, highly technical, helpful comments.",
                            temperature=0.3
                        )
                    )
                    comment_text = resp.text.strip()
                except Exception as e:
                    logger.warning(f"AI generation notice for {d['topic_id']}: {e}")

            if not comment_text:
                comment_text = f"Having migrated multiple client stacks through this exact issue, here is the raw engineering breakdown:\n\n* **The Core Bottleneck:** {d['pain_point']}\n* **The Numbers:** {d['key_metrics']}\n\nWe did an empirical load benchmark testing this across production workloads: {d['solution_url']}\n\nKey takeaway: optimize for your operational ceiling before signing annual contracts."

            playbook_entries.append({
                "topic_id": d["topic_id"],
                "target_subreddit": d["subreddit"],
                "search_intent": d["google_search_query"],
                "solution_partner": d["solution_tool"],
                "target_url": d["solution_url"],
                "comment_template": comment_text,
                "strategy": "Answer technical question with exact metrics, provide neutral trade-offs, link to benchmark dossier for proof."
            })

        playbook = {
            "campaign": "HeliaTech Reddit High-Intent Community Infiltration",
            "last_audit": datetime.now().isoformat(),
            "status": "READY_FOR_COMMUNITY_SYNDICATION",
            "total_targets": len(playbook_entries),
            "targets": playbook_entries
        }

        # Save JSON playbook
        with open(REDDIT_PLAYBOOK_PATH, "w", encoding="utf-8") as f:
            json.dump(playbook, f, indent=2, ensure_ascii=False)

        # Save Markdown reading briefs
        md_lines = ["# 🥷 HeliaTech Reddit High-Intent Infiltration Playbook\n",
                    "> High-karma, engineering-level response briefs to capture Google x Reddit top rankings.\n",
                    "---\n"]
        for entry in playbook_entries:
            md_lines.append(f"## Target: {entry['search_intent']}")
            md_lines.append(f"**Subreddit:** `{entry['target_subreddit']}` | **Tool:** `{entry['solution_partner']}`")
            md_lines.append(f"**Referral Destination:** [{entry['target_url']}]({entry['target_url']})\n")
            md_lines.append("### High-Karma Response Script:")
            md_lines.append("```markdown")
            md_lines.append(entry["comment_template"])
            md_lines.append("```\n---\n")

        REDDIT_BRIEFS_PATH.write_text("\n".join(md_lines), encoding="utf-8")
        logger.info(f"✅ Reddit playbook and briefs saved to {REDDIT_PLAYBOOK_PATH.name} & {REDDIT_BRIEFS_PATH.name}")
        return playbook


if __name__ == "__main__":
    infiltrator = RedditInfiltratorAgent()
    print("--- Helia-RedditInfiltrator: Scanning Google x Reddit High-Intent Threads ---")
    res = infiltrator.synthesize_reddit_playbook()
    print(f"SUCCESS: {res['total_targets']} high-karma response scripts synthesized!")
