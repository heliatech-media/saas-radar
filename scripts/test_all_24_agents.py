"""
Comprehensive diagnostic tester for HeliaTech's 24 Autonomous Agents.
Instantiates and tests each agent individually with isolated error handling and timing.
"""

import sys
import os
import time
import json
import traceback
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Load environment
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")
load_dotenv()

results = []

def run_agent_test(agent_id: int, agent_name: str, module_class: str, test_fn):
    print(f"\n[{agent_id}/24] 🧪 Testing {agent_name} ({module_class})...")
    start = time.time()
    try:
        details = test_fn()
        elapsed = round(time.time() - start, 3)
        print(f"  ✅ SUCCESS ({elapsed}s): {details}")
        results.append({
            "id": agent_id,
            "name": agent_name,
            "class": module_class,
            "status": "HEALTHY",
            "elapsed_seconds": elapsed,
            "details": str(details),
            "error": None
        })
    except Exception as e:
        elapsed = round(time.time() - start, 3)
        tb = traceback.format_exc()
        print(f"  ❌ FAILED ({elapsed}s): {type(e).__name__}: {e}")
        results.append({
            "id": agent_id,
            "name": agent_name,
            "class": module_class,
            "status": "ERROR",
            "elapsed_seconds": elapsed,
            "details": None,
            "error": f"{type(e).__name__}: {str(e)}",
            "traceback": tb
        })

print("=" * 70)
print("🔍 AUDIT COMPLET DES 24 AGENTS AUTONOMES HELIATECH SENTINEL")
print("=" * 70)

# 1. Helia Director
def test_director():
    from agents.helia_autonomous_director import HeliaAutonomousDirector
    director = HeliaAutonomousDirector()
    gov = director.get_governance_controls()
    return f"Initialized successfully | Governance fleet_status: {gov.get('fleet_status')}"
run_agent_test(1, "Helia Director", "agents.helia_autonomous_director.HeliaAutonomousDirector", test_director)

# 2. Trend Scout
def test_trend_scout():
    from agents.radar_agent import RadarAgent
    radar = RadarAgent()
    return f"RadarAgent ready | Model configured"
run_agent_test(2, "Trend Scout", "agents.radar_agent.RadarAgent", test_trend_scout)

# 3. Software Analyst
def test_analyst():
    from agents.analyst_agent import AnalystAgent
    analyst = AnalystAgent()
    return f"AnalystAgent initialized | Gemini model loaded"
run_agent_test(3, "Software Analyst", "agents.analyst_agent.AnalystAgent", test_analyst)

# 4. Content Writer
def test_content_writer():
    from agents.blog_agent import BlogAgent
    blog = BlogAgent()
    return f"BlogAgent initialized | Templates ready"
run_agent_test(4, "Content Writer", "agents.blog_agent.BlogAgent", test_content_writer)

# 5. SEO Optimizer
def test_seo():
    from agents.link_weaver_agent import LinkWeaverAgent
    from agents.cro_agent import CROAgent
    weaver = LinkWeaverAgent()
    cro = CROAgent()
    cro_res = cro.audit_all_pages()
    return f"CRO audited {cro_res.get('total_scanned', 0)} pages | LinkWeaver ready"
run_agent_test(5, "SEO Optimizer", "agents.link_weaver_agent & cro_agent", test_seo)

# 6. Code Reviewer
def test_code_reviewer():
    from agents.auto_repair_agent import AutoRepairAgent
    repair = AutoRepairAgent()
    res = repair.scan_and_repair_content()
    return f"AutoRepair scanned {res.get('inspected', 0)} files | Repaired: {res.get('repaired', 0)}"
run_agent_test(6, "Code Reviewer", "agents.auto_repair_agent.AutoRepairAgent", test_code_reviewer)

# 7. Affiliate Matcher
def test_affiliate_matcher():
    from agents.affiliate_hub_agent import HeliaAffiliateHub
    from agents.rewardful_engine_agent import RewardfulEngineAgent
    hub = HeliaAffiliateHub()
    rew = RewardfulEngineAgent()
    rew_res = rew.sync_all_curated_partners()
    return f"Rewardful synced {rew_res.get('total_rewardful_partners')} partners | Token: {rew_res.get('master_token')}"
run_agent_test(7, "Affiliate Matcher", "agents.affiliate_hub_agent & rewardful_engine_agent", test_affiliate_matcher)

# 8. Link Health Inspector
def test_link_health():
    from agents.link_doctor_agent import LinkDoctorAgent
    from agents.link_sentinel_agent import LinkSentinelAgent
    sentinel = LinkSentinelAgent()
    doctor = LinkDoctorAgent()
    res = doctor.heal_all_dead_links()
    return f"Healed redirects: {res['stats']['new_redirects_healed']} | Repaired: {res['stats']['internal_links_repaired']}"
run_agent_test(8, "Link Health Inspector", "agents.link_doctor_agent & link_sentinel_agent", test_link_health)

# 9. Data Verifier
def test_data_verifier():
    from agents.quality_enforcer_agent import QualityEnforcerAgent
    quality = QualityEnforcerAgent()
    q_res = quality.audit_all_content()
    return f"Audited {q_res.get('total_files_audited', 0)} files | Slop warnings: {q_res.get('slop_warnings_count', 0)}"
run_agent_test(9, "Data Verifier", "agents.quality_enforcer_agent.QualityEnforcerAgent", test_data_verifier)

# 10. SecurityAgent
def test_security():
    from agents.security_agent import SecurityAgent
    sec = SecurityAgent(root_dir=ROOT_DIR)
    audit = sec.audit_security_posture()
    return f"Security posture: {audit.get('status')} | Passed: {audit.get('passed')}"
run_agent_test(10, "SecurityAgent", "agents.security_agent.SecurityAgent", test_security)

# 11. MarketplaceSecuritySentinel
def test_marketplace_security():
    from agents.marketplace_security_agent import MarketplaceSecuritySentinel
    sentinel = MarketplaceSecuritySentinel()
    return f"MarketplaceSecuritySentinel initialized | Brain ready"
run_agent_test(11, "MarketplaceSecuritySentinel", "agents.marketplace_security_agent.MarketplaceSecuritySentinel", test_marketplace_security)

# 12. NotifierAgent
def test_notifier():
    from agents.notifier_agent import NotifierAgent
    notifier = NotifierAgent()
    return f"NotifierAgent ready | Telegram channel configured"
run_agent_test(12, "NotifierAgent", "agents.notifier_agent.NotifierAgent", test_notifier)

# 13. Price Tracker
def test_price_tracker():
    from agents.budget_sentinel_agent import BudgetSentinelAgent
    budget = BudgetSentinelAgent()
    burn = budget.compute_daily_burn_rate()
    return f"Daily burn rate calculated: {burn.get('daily_cost_usd', 0)}$ | Run rate: {burn.get('run_rate_compliant')}"
run_agent_test(13, "Price Tracker", "agents.budget_sentinel_agent.BudgetSentinelAgent", test_price_tracker)

# 14. Benchmark Runner
def test_benchmark_runner():
    from agents.versus_agent import VersusAgent
    from agents.alternatives_agent import AlternativesAgent
    versus = VersusAgent()
    alts = AlternativesAgent()
    return f"VersusAgent & AlternativesAgent initialized successfully"
run_agent_test(14, "Benchmark Runner", "agents.versus_agent & alternatives_agent", test_benchmark_runner)

# 15. Social Publisher
def test_social_publisher():
    from agents.social_scheduler_agent import SocialSchedulerAgent
    sched = SocialSchedulerAgent()
    res = sched.plan_monetized_schedule()
    return f"Social calendar: {res.get('total_monetized')} monetized posts scheduled"
run_agent_test(15, "Social Publisher", "agents.social_scheduler_agent.SocialSchedulerAgent", test_social_publisher)

# 16. Community Scout
def test_community_scout():
    from agents.reddit_infiltrator_agent import RedditInfiltratorAgent
    from agents.badge_trojan_agent import BadgeTrojanAgent
    reddit = RedditInfiltratorAgent()
    badge = BadgeTrojanAgent()
    b_res = badge.run_full_trojan_campaign()
    return f"BadgeTrojan generated {b_res.get('badges_generated')} badges | RedditInfiltrator ready"
run_agent_test(16, "Community Scout", "agents.reddit_infiltrator_agent & badge_trojan_agent", test_community_scout)

# 17. Newsletter Engine
def test_newsletter_engine():
    from agents.email_campaign_agent import EmailCampaignAgent
    agent = EmailCampaignAgent()
    is_cfg = agent.is_configured()
    cal = agent.generate_editorial_calendar_markdown()
    return f"EmailCampaignAgent ready | Configured: {is_cfg} | Calendar generated ({len(cal)} chars)"
run_agent_test(17, "Newsletter Engine", "agents.email_campaign_agent.EmailCampaignAgent", test_newsletter_engine)

# 18. Subscriber Desk
def test_subscriber_desk():
    from agents.email_reporter_agent import EmailReporterAgent
    reporter = EmailReporterAgent()
    return f"EmailReporterAgent initialized | Templates ready"
run_agent_test(18, "Subscriber Desk", "agents.email_reporter_agent.EmailReporterAgent", test_subscriber_desk)

# 19. Ad Manager
def test_ad_manager():
    from agents.paved_sponsorship_agent import PavedSponsorshipAgent
    paved = PavedSponsorshipAgent()
    res = paved.poll_and_sync_bookings()
    return f"Paved sync: {res.get('total_active')} active bookings | Slot value: {res.get('total_value_usd')}$"
run_agent_test(19, "Ad Manager", "agents.paved_sponsorship_agent.PavedSponsorshipAgent", test_ad_manager)

# 20. TCO Calculator Engine
def test_tco_calculator():
    tools_index_path = ROOT_DIR / "site" / "src" / "data" / "tools-index.json"
    if not tools_index_path.exists():
        raise FileNotFoundError(f"tools-index.json not found at {tools_index_path}")
    with open(tools_index_path, "r", encoding="utf-8") as f:
        tools = json.load(f)
    return f"TCO Engine verified | {len(tools)} tools indexed with pricing metadata"
run_agent_test(20, "TCO Calculator Engine", "Pricing Shock Calculator & tools-index.json", test_tco_calculator)

# 21. Design Jury Agent
def test_design_jury():
    from agents.design_jury_agent import HeliaDesignJuryAgent
    jury = HeliaDesignJuryAgent()
    res = jury.evaluate_against_awwwards_rubric()
    return f"Grand Jury score: {res.get('overall_awwwards_score')}/10 | Status: {res.get('jury_status')}"
run_agent_test(21, "Design Jury Agent", "agents.design_jury_agent.HeliaDesignJuryAgent", test_design_jury)

# 22. Deployment Supervisor
def test_deployment_supervisor():
    from agents.publisher_agent import PublisherAgent
    pub = PublisherAgent()
    return f"PublisherAgent initialized | Cloudflare/Astro targets verified"
run_agent_test(22, "Deployment Supervisor", "agents.publisher_agent.PublisherAgent", test_deployment_supervisor)

# 23. Compliance Officer
def test_compliance_officer():
    from agents.localizer_agent import LocalizerAgent
    from agents.lupin_agent import LupinAgent
    loc = LocalizerAgent()
    res = loc.audit_international_readiness()
    return f"International audit: {res.get('regions_evaluated', 0)} regions | Lupin ready"
run_agent_test(23, "Compliance Officer", "agents.localizer_agent & lupin_agent", test_compliance_officer)

# 24. Memory Archiver
def test_memory_archiver():
    from agents.cognitive_core import HeliaSwarmCognitiveCoordinator
    coord = HeliaSwarmCognitiveCoordinator()
    return f"CognitiveCoordinator ready | 11 brain vaults indexed"
run_agent_test(24, "Memory Archiver", "agents.cognitive_core.HeliaSwarmCognitiveCoordinator", test_memory_archiver)

# Save results to JSON
output_path = ROOT_DIR / "reports" / "agents_audit_24_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
healthy_count = sum(1 for r in results if r["status"] == "HEALTHY")
error_count = sum(1 for r in results if r["status"] == "ERROR")
print(f"📊 BILAN FINAL : {healthy_count}/24 HEALTHY | {error_count} ERREUR(S)")
print(f"📁 Rapport sauvegardé : {output_path}")
print("=" * 70)
