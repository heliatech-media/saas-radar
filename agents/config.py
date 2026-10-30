"""
Configuration & Environment Settings for the Multi-Agent System.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT_DIR / "agents"
SITE_DIR = ROOT_DIR / "site"
CONTENT_DIR = SITE_DIR / "src" / "content" / "reviews"
BLOG_CONTENT_DIR = SITE_DIR / "src" / "content" / "blog"
DATA_DIR = SITE_DIR / "src" / "data"

# Load environment variables
load_dotenv(ROOT_DIR / ".env")
load_dotenv()

# Gemini API Key (Can be set via .env or system environment)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEVTO_API_KEY = os.getenv("DEVTO_API_KEY", "")

# Default Model as per Google GenAI SDK standards
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Target High-Margin SaaS Niches with high recurring affiliate payouts
TARGET_NICHES = [
    {
        "category": "AI Automation & No-Code",
        "description": "Workflow builders, chatbots, webhook connectors",
        "commission_range": "20% - 40% recurring",
        "seed_tools": ["Make", "Zapier", "n8n", "Retool", "Voiceflow", "Airtable"]
    },
    {
        "category": "AI Video & Content Creation",
        "description": "Faceless video, avatar generation, repurposing, AI voice",
        "commission_range": "25% - 35% recurring",
        "seed_tools": ["HeyGen", "ElevenLabs", "Descript", "CapCut Pro", "OpusClip", "Runway"]
    },
    {
        "category": "B2B Sales & CRM Intelligence",
        "description": "Cold email automation, lead enrichment, CRM",
        "commission_range": "30% - 50% recurring",
        "seed_tools": ["HubSpot", "Instantly.ai", "Apollo.io", "Close CRM", "Clay.com", "Lemlist"]
    },
    {
        "category": "AI SEO & Copywriting",
        "description": "Content rankers, programmatic SEO, keyword tracking",
        "commission_range": "20% - 30% recurring",
        "seed_tools": ["Surfer SEO", "Semrush", "Jasper", "WriteSonic", "Ahrefs", "KoalaWriter"]
    },
    {
        "category": "Viral Creator & Stripe SaaS (Rewardful Ecosystem)",
        "description": "Viral AI audio/video repurposing, podcast studios, newsletters & memberships natively powered by Rewardful with instant ?via=heliatech tracking",
        "commission_range": "25% - 50% recurring Stripe MRR",
        "seed_tools": ["Castmagic", "Transistor-fm", "Riverside-fm", "Podia", "Memberstack", "VEED-IO", "Opus-Clip", "Beehiiv", "Getimg-ai"]
    }
]

# Affiliate links map: Map tool name to your tracking URL (when you register)
# If no affiliate URL is registered yet, it defaults to the official site.
AFFILIATE_MAP = {
    "elevenlabs": "https://try.elevenlabs.io/ajhd6t7k04dh",
    "make": "https://www.make.com/en/register?pc=heliatechmake",
    "adcreative-ai": "https://www.adcreative.ai/?fp_ref=heliatech",
    "airtable": "https://airtable.com/?ref=heliatech",
    "apollo-io": "https://apollo.grsm.io/heliatech",
    "beehiiv": "https://www.beehiiv.com/?via=heliatech",
    "brevo": "https://brevo.partnerlinks.io/heliatech",
    "castmagic": "https://castmagic.io/?via=heliatech",
    "clickup": "https://clickup.pxf.io/c/heliatech",
    "cursor": "https://www.cursor.com/?via=heliatech",
    "getimg-ai": "https://getimg.ai/?via=heliatech",
    "heygen": "https://heygen.grsm.io/heliatech",
    "linear": "https://linear.app/?via=heliatech",
    "lusha": "https://lusha.grsm.io/heliatech",
    "memberstack": "https://www.memberstack.com/?via=heliatech",
    "monday-com": "https://monday.com/?ref=heliatech",
    "framer": "https://framer.partnerstack.com/heliatech",
    "n8n": "https://n8n.io/?via=heliatech",
    "lemlist": "https://lemlist.com/?via=heliatech",
    "notion-ai": "https://www.notion.so/?ref=heliatech",
    "opus-clip": "https://www.opus.pro/?via=heliatech",
    "partnerstack": "https://partnerstack.com/?via=heliatech",
    "phantombuster": "https://phantombuster.com/?via=heliatech",
    "podia": "https://www.podia.com/?via=heliatech",
    "printify": "https://printify.pxf.io/c/heliatech",
    "retool": "https://retool.grsm.io/heliatech",
    "rewardful": "https://www.rewardful.com/?via=heliatech/?via=heliatech",
    "tweethunter": "https://tweethunter.io/?via=helia",
    "riverside-fm": "https://riverside.fm/?via=heliatech",
    "transistor-fm": "https://transistor.fm/?via=heliatech",
    "veed-io": "https://www.veed.io/?via=heliatech",
    "lovable": "https://lovable.dev/?via=heliatech",
    "supabase": "https://supabase.com/?via=heliatech",
    "typeform": "https://typeform.grsm.io/heliatech",
    "vercel": "https://vercel.com/?via=heliatech",
    "jasper-ai": "https://partnerstack.com/jasper?via=heliatech",
    "voiceflow": "https://voiceflow.grsm.io/heliatech",
    "wati": "https://www.wati.io/?fp_ref=heliatech",
    "webflow": "https://webflow.pxf.io/c/heliatech",
    "zapier": "https://zapier.com/app/register?via=heliatech",
    "transistor": "https://transistor.fm/?via=heliatech",
    "podcastle": "https://podcastle.grrow.co/?via=heliatech",
    "peripety": "https://www.peripety.ai/?via=heliatech",
    "resend": "https://resend.com/?via=heliatech",
    "riverside": "https://riverside.fm/?via=heliatech",
    "tally": "https://tally.so/?via=heliatech",
    "tome": "https://tome.app/?via=heliatech",
    "veed": "https://www.veed.io/?via=heliatech",
    "klap": "https://klap.app/?via=heliatech",
    "v0": "https://v0.dev/?via=heliatech",
    "minicong": "https://minicong.ai/?via=heliatech",
    "dumpling-ai": "https://www.dumpling.ai/?via=heliatech",
    "julius-ai": "https://julius.ai/?via=heliatech",
    "sanity": "https://www.sanity.io/?ref=heliatech",
    "klaviyo": "https://partnerstack.com/klaviyo?via=heliatech"
}
