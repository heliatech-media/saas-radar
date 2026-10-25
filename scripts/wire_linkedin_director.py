"""
Wire LinkedInSyndicator into agents/helia_autonomous_director.py
"""
from pathlib import Path

path = Path("agents/helia_autonomous_director.py")
content = path.read_text(encoding="utf-8")

# 1. Add import
if "from agents.linkedin_syndication_agent import LinkedInSyndicator" not in content:
    content = content.replace(
        "from agents.devto_syndication_agent import syndicate_next_monetized_article",
        "from agents.devto_syndication_agent import syndicate_next_monetized_article\nfrom agents.linkedin_syndication_agent import LinkedInSyndicator"
    )

# 2. Add instantiation in __init__
if "self.linkedin_syndicator = LinkedInSyndicator()" not in content:
    content = content.replace(
        "self.news_sniffer = BreakingNewsSnifferAgent(api_key=api_key)",
        "self.news_sniffer = BreakingNewsSnifferAgent(api_key=api_key)\n        self.linkedin_syndicator = LinkedInSyndicator()"
    )

# 3. Add Step 6.19 in execute_autonomous_growth_cycle
step_6_19 = """        # Step 6.19: Sub-Agent LinkedInSyndicator (Automated 2-3 Posts/Day on LinkedIn)
        try:
            self.log("Helia-LinkedInSyndicator", "Broadcasting next monetized 'Standard Emblème' breakdown to LinkedIn...", "💼")
            li_res = self.linkedin_syndicator.syndicate_next_article()
            if li_res.get("status") == "SUCCESS":
                self.log("Helia-LinkedInSyndicator", f"Published live to LinkedIn: {li_res['slug']} | URN: {li_res['share_urn']}", "🌟")
            else:
                self.log("Helia-LinkedInSyndicator", f"LinkedIn syndicator status: {li_res.get('status', 'Standby')}", "📋")
        except Exception as e:
            self.log("Helia-LinkedInSyndicator", f"LinkedIn syndicator notice: {e}", "⚠️")
"""

if "Helia-LinkedInSyndicator" not in content:
    content = content.replace(
        "        # Step 7: Sub-Agent EdgePublisher",
        step_6_19 + "\n        # Step 7: Sub-Agent EdgePublisher"
    )

path.write_text(content, encoding="utf-8")
print("[OK] Wired LinkedInSyndicator into HeliaAutonomousDirector!")
