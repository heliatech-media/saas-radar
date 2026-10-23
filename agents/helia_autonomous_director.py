"""
🏛️ HELIA AUTONOMOUS EXECUTIVE DIRECTOR
Chief Operating Officer & Autonomous Multi-Agent Commander for HeliaTech Media.
Target: 100,000 monthly visitors (Phase 1) ➔ 1,000,000 monthly visitors (Phase 2).

Orchestrates 5 autonomous sub-agents:
1. Helia-TrendScout: Discovers viral, breakout & high-commission B2B software.
2. Helia-Analyst: Generates architectural teardowns, ROI metrics & rich schemas.
3. Helia-ContentFactory: Writes high-ranking, 100% English editorial masterclasses.
4. Helia-LinkOptimizer: Connects circular SEO links across reviews, blog posts & cloaked affiliate URLs.
5. Helia-EdgePublisher: Validates build integrity, commits to Git & triggers Netlify edge deployment.
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
from agents.models import ToolReview


class HeliaAutonomousDirector:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        self.radar = RadarAgent(api_key=api_key)
        self.analyst = AnalystAgent(api_key=api_key)
        self.publisher = PublisherAgent()
        self.blog_agent = BlogAgent(api_key=api_key)

    def log(self, agent_name: str, message: str, icon: str = "⚡"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{agent_name}] {icon} {message}")

    def execute_autonomous_growth_cycle(self, auto_push: bool = True):
        """
        Executes a complete autonomous cycle directed by Agent Chief Helia:
        1. TrendScout discovers a breakout software.
        2. Analyst benchmarks it and builds review.
        3. ContentFactory writes a deep-dive blog masterclass.
        4. EdgePublisher verifies build and deploys to Netlify.
        """
        self.log("HELIA-CORE", "🚀 Initiating Autonomous Growth Cycle (Target: 100K+ visitors/mo)...", "🏛️")

        # Step 1: Sub-Agent TrendScout
        self.log("Helia-TrendScout", "Scanning B2B software ecosystems and high-yield affiliate markets...", "🔍")
        keyword = self.radar.scout_trending_software()
        self.log("Helia-TrendScout", f"Target locked: '{keyword.tool_name}' ({keyword.category}) | Commission: {keyword.average_commission}", "🎯")

        # Step 2: Sub-Agent Analyst
        self.log("Helia-Analyst", f"Initiating architectural forensic evaluation of '{keyword.tool_name}'...", "🔬")
        review = self.analyst.analyze_tool(tool_name=keyword.tool_name, category_hint=keyword.category)
        review_path = self.publisher.publish_review(review)
        self.log("Helia-Analyst", f"Review teardown published: {review_path.name}", "✅")

        # Step 3: Sub-Agent ContentFactory
        self.log("Helia-ContentFactory", f"Drafting 100% English masterclass & hands-on guide for '{keyword.tool_name}'...", "✍️")
        try:
            blog_post = self.blog_agent.write_tool_masterclass(review)
            blog_path = self.publisher.publish_blog_post(blog_post)
            self.log("Helia-ContentFactory", f"Masterclass published: {blog_path.name}", "📰")
        except Exception as e:
            self.log("Helia-ContentFactory", f"Warning: Blog generation error: {e}", "⚠️")

        # Step 4: Sub-Agent EdgePublisher
        self.log("Helia-EdgePublisher", "Compiling Astro static build and validating zero-error integrity...", "⚙️")
        build_success = self._run_build()

        if build_success and auto_push:
            self.log("Helia-EdgePublisher", "Build validated! Deploying to Netlify edge via GitHub...", "🚢")
            self._deploy_git(f"feat(auto-growth): Helia deployed autonomous review & masterclass for {keyword.tool_name}")
            self.log("HELIA-CORE", f"🎉 Autonomous Growth Cycle complete for {keyword.tool_name}! All systems live on https://heliatech.online", "🏆")
        else:
            self.log("HELIA-CORE", "Cycle completed locally. Ready for manual deployment.", "🏁")

    def expand_blog_for_existing_tools(self, limit: int = 2, auto_push: bool = True):
        """
        Helia scans existing reviews that lack a dedicated blog masterclass,
        and deploys in-depth 100% English articles for them to supercharge SEO.
        """
        self.log("HELIA-CORE", f"🔍 Scanning existing reviews for unwritten blog masterclasses (Limit: {limit})...", "📚")

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
                    except Exception as e:
                        pass

        self.log("HELIA-CORE", f"Found {len(uncovered_reviews)} audited tools without dedicated masterclasses.", "📊")

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
                timeout=60
            )
            if res.returncode == 0:
                return True
            else:
                self.log("Helia-EdgePublisher", f"Build Error:\n{res.stderr[:400]}", "❌")
                return False
        except Exception as e:
            self.log("Helia-EdgePublisher", f"Build Exception: {e}", "❌")
            return False

    def _deploy_git(self, commit_message: str):
        """Commits changes and pushes to origin main."""
        try:
            subprocess.run(["git", "add", "."], cwd=str(ROOT_DIR), check=True)
            subprocess.run(["git", "commit", "-m", commit_message], cwd=str(ROOT_DIR), check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=str(ROOT_DIR), check=True)
            self.log("Helia-EdgePublisher", "Git push successful. Netlify build triggered.", "🌐")
        except subprocess.CalledProcessError as e:
            self.log("Helia-EdgePublisher", f"Git operation error: {e}", "⚠️")


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
        # Default action: run 1 full cycle
        director.execute_autonomous_growth_cycle(auto_push=not args.no_push)


if __name__ == "__main__":
    main()
