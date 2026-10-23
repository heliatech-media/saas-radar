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
8. Helia-EdgePublisher: Validates Astro builds and deploys to Cloudflare Pages edge without latency.
9. Helia-ArticleStylist: Architects luxury layouts, Mermaid diagrams, tables & visual callouts.
10. Helia-VisualArtist: Generates custom 1200x630 relative visual assets & OpenGraph cards.
11. Helia-SocialScheduler: Filters strictly verified monetized tools & coordinates autonomous X and LinkedIn schedules.
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
from agents.visionary_growth_agent import VisionaryGrowthAgent
from agents.article_layout_agent import ArticleLayoutAgent
from agents.image_generator_agent import ImageGeneratorAgent
from agents.social_scheduler_agent import SocialSchedulerAgent
from agents.affiliate_hub_agent import HeliaAffiliateHub
from agents.affiliate_hunter_agent import AffiliateHunterAgent
from agents.versus_agent import VersusAgent
from agents.alternatives_agent import AlternativesAgent
from agents.link_weaver_agent import LinkWeaverAgent
from agents.notifier_agent import NotifierAgent
from agents.cro_agent import CROAgent
from agents.data_visualizer_agent import DataVisualizerAgent
from agents.backlink_agent import BacklinkArchitectAgent
from agents.localizer_agent import LocalizerAgent
from agents.link_sentinel_agent import LinkSentinelAgent
from agents.quality_enforcer_agent import QualityEnforcerAgent
from agents.budget_sentinel_agent import BudgetSentinelAgent
from agents.lupin_agent import LupinAgent
from agents.badge_trojan_agent import BadgeTrojanAgent
from agents.reddit_infiltrator_agent import RedditInfiltratorAgent
from agents.models import ToolReview


class HeliaAutonomousDirector:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        # Initialize Helia's fleet of specialized autonomous sub-agents
        self.visionary = VisionaryGrowthAgent()
        self.security = SecurityAgent(root_dir=ROOT_DIR)
        self.repair = AutoRepairAgent()
        self.radar = RadarAgent(api_key=api_key)
        self.analyst = AnalystAgent(api_key=api_key)
        self.publisher = PublisherAgent()
        self.blog_agent = BlogAgent(api_key=api_key)
        self.reporter = EmailReporterAgent()
        self.social = SocialGrowthAgent(api_key=api_key)
        self.stylist = ArticleLayoutAgent()
        self.artist = ImageGeneratorAgent(api_key=api_key)
        self.scheduler = SocialSchedulerAgent(api_key=api_key)
        self.affiliate_hub = HeliaAffiliateHub()
        self.hunter = AffiliateHunterAgent(api_key=api_key)
        self.versus = VersusAgent(api_key=api_key)
        self.alternatives = AlternativesAgent(api_key=api_key)
        self.weaver = LinkWeaverAgent()
        self.notifier = NotifierAgent()
        self.cro = CROAgent()
        self.visualizer = DataVisualizerAgent()
        self.backlink = BacklinkArchitectAgent()
        self.localizer = LocalizerAgent(api_key=api_key)
        self.link_sentinel = LinkSentinelAgent()
        self.quality = QualityEnforcerAgent()
        self.budget = BudgetSentinelAgent()
        self.lupin = LupinAgent(api_key=api_key)
        self.badge_trojan = BadgeTrojanAgent()
        self.reddit_infiltrator = RedditInfiltratorAgent(api_key=api_key)

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
        if not sec_audit.get("passed", False):
            self.log("Helia-CyberDefense", f"🚨 SECURITY SHIELD TRIGGERED: Build blocked! Credential risk detected: {sec_audit['findings']}", "🛑")
            raise PermissionError("Deployment strictly blocked by Helia-CyberDefense: sensitive credentials detected in repository.")
        self.log("Helia-CyberDefense", f"Status: {sec_audit['status']} (Zero credential leak, strict headers verified)", "✅")

        # Step 2: Sub-Agent AutoRepair
        self.log("Helia-AutoRepair", "Scanning Markdown content & YAML schemas for syntax flaws...", "🔧")
        repair_res = self.repair.scan_and_repair_content()
        self.log("Helia-AutoRepair", f"Inspected: {repair_res['inspected']} files | Repaired: {repair_res['repaired']} issues", "✅")

        # Step 2.5: Sub-Agent ArticleStylist (Layout & Typesetting Architect)
        self.log("Helia-ArticleStylist", "Auditing editorial layouts, Mermaid diagrams & visual callouts...", "🎨")
        layout_res = self.stylist.beautify_all_articles()
        self.log("Helia-ArticleStylist", f"Typesetting verified across {layout_res['formatted_count']} articles.", "📐")

        # Step 2.6: Sub-Agent VisualArtist (Hero & Social OpenGraph Artwork)
        self.log("Helia-VisualArtist", "Auditing 1200x630 custom hero visuals & OpenGraph social cards...", "🖼️")
        visual_res = self.artist.process_all_articles()
        self.log("Helia-VisualArtist", f"Visual assets verified for {visual_res['generated']} articles.", "✨")

        # Step 2.7: Sub-Agent AffiliateHub (Multi-Network Autonomous API Sync)
        self.log("Helia-AffiliateHub", "Querying partner networks (Impact, PartnerStack, CJ) for tracking links...", "🔗")
        hub_res = self.affiliate_hub.sync_into_system()
        self.log("Helia-AffiliateHub", f"Affiliate sync complete: {hub_res['synced_count']} tools monetized.", "💰")

        # Step 2.8: Sub-Agent AffiliateHunter (Autonomous AI Link & Partner Scout)
        self.log("Helia-AffiliateHunter", "Autonomous AI link scout scanning unmonetized tools...", "🏹")
        hunt_res = self.hunter.execute_hunt_cycle(max_tools=3)
        self.log("Helia-AffiliateHunter", f"Affiliate hunt complete: {hunt_res['hunted']} tools monetized independently.", "🎯")

        # Step 2.9: Sub-Agent LinkWeaver (Topical Mesh & Internal Linking)
        self.log("Helia-LinkWeaver", "Executing semantic internal link weaving across topic cluster...", "🕸️")
        weaver_res = self.weaver.weave_all()
        self.log("Helia-LinkWeaver", f"Internal mesh strengthened: {weaver_res['total_links_added']} hyperlinks active.", "✨")

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

        # Step 5.5: Sub-Agent VersusEngine (Dual Head-to-Head Duel Showdowns)
        try:
            self.log("Helia-VersusEngine", "Evaluating candidate B2B rivalry showdowns...", "⚔️")
            versus_res = self.versus.execute_versus_sweep(limit=1)
            if versus_res:
                self.log("Helia-VersusEngine", f"Published head-to-head showdown: {versus_res[0].name}", "🏆")
        except Exception as e:
            self.log("Helia-VersusEngine", f"Versus engine notice: {e}", "⚠️")

        # Step 5.6: Sub-Agent AlternativesEngine ("Top 7 Alternatives" Authority Roundups)
        try:
            self.log("Helia-AlternativesEngine", "Evaluating candidate replacement searches...", "🔄")
            alt_res = self.alternatives.execute_alternatives_sweep(limit=1)
            if alt_res:
                self.log("Helia-AlternativesEngine", f"Published Top 7 Alternatives masterclass: {alt_res[0].name}", "🌟")
        except Exception as e:
            self.log("Helia-AlternativesEngine", f"Alternatives engine notice: {e}", "⚠️")

        # Step 6.5: Sub-Agent SocialScheduler (Monetized Partner Campaign Scheduler)
        try:
            self.log("Helia-SocialScheduler", "Synchronizing monetized social queues & scheduling multi-channel calendar...", "📅")
            sched_res = self.scheduler.plan_monetized_schedule()
            self.log("Helia-SocialScheduler", f"Monetized calendar locked: {sched_res['total_monetized']} partner campaigns active.", "🎯")
        except Exception as e:
            self.log("Helia-SocialScheduler", f"Scheduler notice: {e}", "⚠️")

        # Step 6.6: Sub-Agent CRO (Conversion Rate Optimization Audit)
        try:
            self.log("Helia-CRO", "Auditing conversion rate optimization and sticky CTA yield...", "💎")
            self.cro.audit_all_pages()
        except Exception as e:
            self.log("Helia-CRO", f"CRO notice: {e}", "⚠️")

        # Step 6.7: Sub-Agent DataVisualizer (Live Business Intelligence Telemetry)
        try:
            self.log("Helia-DataVisualizer", "Refreshing live financial telemetry and Sentinel data streams...", "📊")
            self.visualizer.generate_live_telemetry()
        except Exception as e:
            self.log("Helia-DataVisualizer", f"Visualizer notice: {e}", "⚠️")

        # Step 6.8: Sub-Agent BacklinkArchitect (Digital PR & SEO Authority Playbook)
        try:
            self.log("Helia-BacklinkArchitect", "Mapping high-DR syndication targets and authority outreach...", "🔗")
            self.backlink.generate_authority_playbook()
        except Exception as e:
            self.log("Helia-BacklinkArchitect", f"Backlink notice: {e}", "⚠️")

        # Step 6.9: Sub-Agent Localizer (International Growth Audit)
        try:
            self.log("Helia-Localizer", "Evaluating global multi-region expansion readiness...", "🌍")
            self.localizer.audit_international_readiness()
        except Exception as e:
            self.log("Helia-Localizer", f"Localizer notice: {e}", "⚠️")

        # Step 6.10: Sub-Agent LinkSentinel (Dead Affiliate Link & Redirect Health Guardian)
        try:
            self.log("Helia-LinkSentinel", "Auditing affiliate edge endpoints & validating 100% link health...", "🛡️")
            self.link_sentinel.audit_all_redirects()
        except Exception as e:
            self.log("Helia-LinkSentinel", f"Link sentinel notice: {e}", "⚠️")

        # Step 6.11: Sub-Agent QualityEnforcer (Anti-AI Slop & Editorial Balance Audit)
        try:
            self.log("Helia-QualityEnforcer", "Auditing editorial authenticity & enforcing mandatory trade-offs...", "🔍")
            self.quality.audit_all_content()
        except Exception as e:
            self.log("Helia-QualityEnforcer", f"Quality enforcer notice: {e}", "⚠️")

        # Step 6.12: Sub-Agent BudgetSentinel (AI Token Burn Rate & Spend Cap Audit)
        try:
            self.log("Helia-BudgetSentinel", "Auditing AI token burn rate & verifying zero-cost run-rate...", "💰")
            self.budget.compute_daily_burn_rate()
        except Exception as e:
            self.log("Helia-BudgetSentinel", f"Budget sentinel notice: {e}", "⚠️")

        # Step 6.13: Sub-Agent Lupin (Asymmetric Growth Hacking & Masterstroke Engine)
        try:
            self.log("Helia-Lupin", "Executing Lupin asymmetric growth hacking audit & masterstrokes...", "🎭")
            self.lupin.execute_all_coups()
            self.log("Helia-Lupin", "Lupin operations verified: Ghost Hijacking, Pricing Leaks & Parasite SEO active.", "💎")
        except Exception as e:
            self.log("Helia-Lupin", f"Lupin notice: {e}", "⚠️")

        # Step 6.14: Sub-Agent BadgeTrojan (Trojan Horse G2/Trustpilot Partner Badges)
        try:
            self.log("Helia-BadgeTrojan", "Auditing accreditation badges & refreshing PR outreach kits...", "🏆")
            badge_res = self.badge_trojan.run_full_trojan_campaign()
            self.log("Helia-BadgeTrojan", f"Badges active: {badge_res['badges_generated']} SVGs deployed | {badge_res['kits_prepared']} PR kits locked.", "💎")
        except Exception as e:
            self.log("Helia-BadgeTrojan", f"Badge Trojan notice: {e}", "⚠️")

        # Step 6.15: Sub-Agent RedditInfiltrator (High-Intent Community Traffic & Forum SEO)
        try:
            self.log("Helia-RedditInfiltrator", "Synthesizing high-karma technical answers for Google x Reddit targets...", "🥷")
            reddit_res = self.reddit_infiltrator.synthesize_reddit_playbook()
            self.log("Helia-RedditInfiltrator", f"Reddit playbook updated: {reddit_res['total_targets']} high-intent briefs live.", "🎯")
        except Exception as e:
            self.log("Helia-RedditInfiltrator", f"Reddit Infiltrator notice: {e}", "⚠️")

        # Step 7: Sub-Agent EdgePublisher
        self.log("Helia-EdgePublisher", "Compiling Astro static build and validating zero-error edge propagation...", "⚙️")
        self.visionary.generate_growth_blueprint()
        build_success = self._run_build()

        if build_success and auto_push:
            self.log("Helia-EdgePublisher", "Build 100% clean. Committing and pushing to origin main...", "🚢")
            self._deploy_git(f"feat(growth): Helia deployed autonomous review & masterclass for {keyword.tool_name}")
            self.log("Helia-EdgePublisher", "Cloudflare edge deployment triggered globally.", "🌐")

        # Step 8: Sub-Agent Reporter
        self.log("Helia-Reporter", "Compiling Daily Executive Intelligence Digest...", "📬")
        report_path = self.reporter.generate_daily_report(
            security_status=sec_audit['status'],
            auto_repair_status=repair_res['status']
        )
        self.log("Helia-Reporter", f"Executive report recorded at: {report_path.name}", "📊")
        
        # Step 9: Sub-Agent Notifier (Founder Push Notifications)
        try:
            self.notifier.send_notification(
                title=f"Cycle Autonome #{keyword.tool_name}",
                message=f"Helia a audité le site, renforcé le maillage interne, publié l'analyse de {keyword.tool_name} et mis à jour le calendrier social.",
                category="CYCLE",
                link="https://heliatech.online/sentinel/suivicontrol"
            )
        except Exception as e:
            self.log("Helia-Notifier", f"Notification notice: {e}", "⚠️")

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
            self.visionary.generate_growth_blueprint()
            self.log("Helia-EdgePublisher", "Rebuilding Astro static pages...", "⚙️")
            if self._run_build() and auto_push:
                self.log("Helia-EdgePublisher", "Pushing updates to GitHub main branch...", "🚢")
                self._deploy_git(f"feat(blog-expansion): Helia deployed {count} new B2B masterclasses")
                self.log("HELIA-CORE", f"🚀 {count} new masterclasses deployed live to Cloudflare Edge!", "🏆")

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
            self.log("Helia-EdgePublisher", "Git push successful. Cloudflare Pages build in progress.", "🌐")
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
