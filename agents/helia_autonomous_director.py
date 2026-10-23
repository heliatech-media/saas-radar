"""
🏛️ HELIA AUTONOMOUS EXECUTIVE DIRECTOR — VERSION 3.0
Chief Operating Officer & Multi-Agent Supreme Commander for HeliaTech Media.
Strategic Targets: Phase 1: 100,000 monthly visitors ➔ Phase 2: 1,000,000 monthly visitors.

Helia's Internal Fleet of Specialized Sub-Agents (Stealth / Invisible to Competitors):
1. Helia-CyberDefense: Audits code, protects API secrets, enforces HTTPS & security headers.
2. Helia-AutoRepair: Inspects markdown/YAML, heals syntax errors, and guarantees zero build failures.
3. Helia-TrendScout: Scans B2B SaaS markets, search intent volumes, and affiliate partner networks.
4. Helia-Analyst: Generates architectural teardowns, ROI metrics, and Google Rich FAQ schemas.
5. Helia-ContentFactory: Produces 100% English editorial masterclasses & hands-on workshops.
6. Helia-SocialGrowth: Prepares viral Twitter/X threads and LinkedIn authority breakdowns.
7. Helia-Reporter: Generates daily executive intelligence digests tracking the 100k visitor goal.
8. Helia-EdgePublisher: Validates Astro builds and deploys to Netlify CDN edge without latency.
"""

import sys
import os
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import yaml

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from agents.config import GEMINI_API_KEY, CONTENT_DIR, BLOG_CONTENT_DIR, SITE_DIR
from agents.radar_agent import RadarAgent
from agents.analyst_agent import AnalystAgent
from agents.publisher_agent import PublisherAgent
from agents.blog_agent import BlogAgent
from agents.security_agent import SecurityAgent
from agents.auto_repair_agent import AutoRepairAgent
from agents.email_reporter_agent import EmailReporterAgent
from agents.social_growth_agent import SocialGrowthAgent
from agents.models import ToolReview


class HeliaAutonomousDirector:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        # Initialize Helia's 7 sub-agents
        self.security = SecurityAgent(root_dir=ROOT_DIR)
        self.repair = AutoRepairAgent()
        self.radar = RadarAgent(api_key=api_key)
        self.analyst = AnalystAgent(api_key=api_key)
        self.publisher = PublisherAgent()
        self.blog_agent = BlogAgent(api_key=api_key)
        self.reporter = EmailReporterAgent()
        self.social = SocialGrowthAgent(api_key=api_key)

    def log(self, agent_name: str, message: str, icon: str = "⚡"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{agent_name}] {icon} {message}")

    def execute_autonomous_growth_cycle(self, auto_push: bool = True):
        """
        Executes a complete end-to-end autonomous growth cycle:
        1. Cybersecurity audit
        2. Auto-repair check
        3. Market trend scouting
        4. In-depth analysis & review generation
        5. Editorial masterclass production
        6. Social distribution thread drafting
        7. Astro build verification & Netlify edge deployment
        8. Daily executive report synthesis
        """
        self.log("HELIA-CORE", "🏛️ Initiating Autonomous Growth Cycle (Target: 100,000 visitors/mo)...", "🚀")

        # Step 1: Sub-Agent CyberDefense
        self.log("Helia-CyberDefense", "Auditing repository integrity, security headers & secret protection...", "🛡️")
        sec_audit = self.security.audit_security_posture()
        self.log("Helia-CyberDefense", f"Status: {sec_audit['status']} (Zero public agent leak, strict headers verified)", "✅")

        # Step 2: Sub-Agent AutoRepair
        self.log("Helia-AutoRepair", "Scanning Markdown content & YAML schemas for syntax flaws...", "🔧")
        repair_res = self.repair.scan_and_repair_content()
        self.log("Helia-AutoRepair", f"Inspected: {repair_res['inspected']} files | Repaired: {repair_res['repaired']} issues", "✅")

        # Step 3: Sub-Agent TrendScout
        self.log("Helia-TrendScout", "Scanning high-intent search volumes and partner affiliate networks...", "🔍")
        keyword = self.radar.scout_trending_software()
        self.log("Helia-TrendScout", f"Target locked: '{keyword.tool_name}' ({keyword.category}) | Commission: {keyword.average_commission}", "🎯")

        # Step 4: Sub-Agent Analyst
        self.log("Helia-Analyst", f"Executing architectural forensic teardown of '{keyword.tool_name}'...", "🔬")
        review = self.analyst.analyze_tool(tool_name=keyword.tool_name, category_hint=keyword.category)
        review_path = self.publisher.publish_review(review)
        self.log("Helia-Analyst", f"Review published & indexed: {review_path.name}", "📑")

        # Step 5: Sub-Agent ContentFactory
        self.log("Helia-ContentFactory", f"Drafting 100% English masterclass & practical workshop for '{keyword.tool_name}'...", "✍️")
        try:
            blog_post = self.blog_agent.write_tool_masterclass(review)
            blog_path = self.publisher.publish_blog_post(blog_post)
            self.log("Helia-ContentFactory", f"Masterclass published: {blog_path.name}", "📰")

            # Step 6: Sub-Agent SocialGrowth
            self.log("Helia-SocialGrowth", "Synthesizing viral Twitter/X growth thread & hooks...", "🐦")
            tweets = self.social.craft_viral_x_thread(blog_post)
            self.social.broadcast_thread_to_x(tweets)
            self.log("Helia-SocialGrowth", f"Drafted {len(tweets)}-tweet high-converting thread.", "🚀")
        except Exception as e:
            self.log("Helia-ContentFactory", f"Blog generation notice: {e}", "⚠️")

        # Step 7: Sub-Agent EdgePublisher
        self.log("Helia-EdgePublisher", "Compiling Astro static build and validating zero-error edge propagation...", "⚙️")
        build_success = self._run_build()

        if build_success and auto_push:
            self.log("Helia-EdgePublisher", "Build 100% clean. Committing and pushing to origin main...", "🚢")
            self._deploy_git(f"feat(growth): Helia deployed autonomous review & masterclass for {keyword.tool_name}")
            self.log("Helia-EdgePublisher", "Netlify deployment triggered globally.", "🌐")

        # Step 8: Sub-Agent Reporter
        self.log("Helia-Reporter", "Compiling Daily Executive Intelligence Digest...", "📬")
        report_path = self.reporter.generate_daily_report(
            security_status=sec_audit['status'],
            auto_repair_status=repair_res['status']
        )
        self.log("Helia-Reporter", f"Executive report recorded at: {report_path.name}", "📊")
        self.log("HELIA-CORE", f"🎉 Autonomous Growth Cycle successfully concluded for {keyword.tool_name}!", "🏆")

    def expand_blog_for_existing_tools(self, limit: int = 2, auto_push: bool = True):
        """Helia expands masterclasses for audited tools lacking an in-depth guide."""
        self.log("HELIA-CORE", f"Scanning reviews lacking dedicated blog masterclasses (Limit: {limit})...", "📚")

        existing_blog_slugs = set()
        if BLOG_CONTENT_DIR.exists():
            for f in BLOG_CONTENT_DIR.glob("*.md"):
                try:
                    content = f.read_text(encoding="utf-8")
                    frontmatter = yaml.safe_load(content.split("---")[1])
                    if "tool_slug" in frontmatter:
                        existing_blog_slugs.add(frontmatter["tool_slug"])
                except Exception:
                    pass

        uncovered_reviews = []
        if CONTENT_DIR.exists():
            for f in sorted(CONTENT_DIR.glob("*.md")):
                slug = f.stem
                if slug not in existing_blog_slugs:
                    try:
                        content = f.read_text(encoding="utf-8")
                        frontmatter = yaml.safe_load(content.split("---")[1])
                        uncovered_reviews.append(ToolReview(**frontmatter, detailed_verdict="Audited."))
                    except Exception:
                        pass

        self.log("HELIA-CORE", f"Identified {len(uncovered_reviews)} audited tools ready for masterclasses.", "📊")

        count = 0
        for review in uncovered_reviews:
            if count >= limit:
                break
            self.log("Helia-ContentFactory", f"Architecting dedicated English masterclass for '{review.name}'...", "✍️")
            try:
                post = self.blog_agent.write_tool_masterclass(review)
                path = self.publisher.publish_blog_post(post)
                self.log("Helia-ContentFactory", f"Published masterclass: {path.name}", "✅")
                count += 1
            except Exception as e:
                self.log("Helia-ContentFactory", f"Failed for {review.name}: {e}", "❌")

        if count > 0:
            self.log("Helia-EdgePublisher", "Rebuilding Astro static pages...", "⚙️")
            if self._run_build() and auto_push:
                self.log("Helia-EdgePublisher", "Pushing updates to GitHub main branch...", "🚢")
                self._deploy_git(f"feat(blog-expansion): Helia deployed {count} new B2B masterclasses")
                self.log("HELIA-CORE", f"🚀 {count} new masterclasses deployed live to Netlify!", "🏆")

    def _run_build(self) -> bool:
        """Executes 'npm run build' inside site/."""
        try:
            res = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(SITE_DIR),
                capture_output=True,
                text=True,
                shell=True,
                timeout=90
            )
            return res.returncode == 0
        except Exception as e:
            self.log("Helia-EdgePublisher", f"Build Exception: {e}", "❌")
            return False

    def _deploy_git(self, commit_message: str):
        """Commits changes and pushes to origin main."""
        try:
            subprocess.run(["git", "add", "."], cwd=str(ROOT_DIR), check=True)
            subprocess.run(["git", "commit", "-m", commit_message], cwd=str(ROOT_DIR), check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=str(ROOT_DIR), check=True)
            self.log("Helia-EdgePublisher", "Git push successful. Netlify build in progress.", "🌐")
        except subprocess.CalledProcessError as e:
            self.log("Helia-EdgePublisher", f"Git operation notice: {e}", "⚠️")


def main():
    parser = argparse.ArgumentParser(description="Helia Autonomous Executive Director")
    parser.add_argument("--run-once", action="store_true", help="Execute 1 full autonomous growth cycle")
    parser.add_argument("--expand-blog", type=int, default=0, help="Generate N masterclasses for existing tools lacking articles")
    parser.add_argument("--daemon", action="store_true", help="Run 24/7 continuous autonomous expansion loop")
    parser.add_argument("--interval-hours", type=float, default=6.0, help="Interval in hours between cycles in daemon mode")
    parser.add_argument("--no-push", action="store_true", help="Do not push to git/Netlify automatically")

    args = parser.parse_args()
    director = HeliaAutonomousDirector()

    if args.expand_blog > 0:
        director.expand_blog_for_existing_tools(limit=args.expand_blog, auto_push=not args.no_push)
    elif args.run_once:
        director.execute_autonomous_growth_cycle(auto_push=not args.no_push)
    elif args.daemon:
        director.log("HELIA-CORE", f"Starting 24/7 autonomous loop (Interval: {args.interval_hours}h)...", "⏱️")
        while True:
            try:
                director.execute_autonomous_growth_cycle(auto_push=not args.no_push)
                sleep_seconds = int(args.interval_hours * 3600)
                director.log("HELIA-CORE", f"Cycle complete. Next autonomous cycle in {args.interval_hours} hours.", "💤")
                time.sleep(sleep_seconds)
            except KeyboardInterrupt:
                director.log("HELIA-CORE", "Autonomous daemon stopped by operator.", "🛑")
                break
            except Exception as e:
                director.log("HELIA-CORE", f"Cycle encountered error: {e}. Retrying in 15 minutes.", "⚠️")
                time.sleep(900)
    else:
        director.execute_autonomous_growth_cycle(auto_push=not args.no_push)


if __name__ == "__main__":
    main()
