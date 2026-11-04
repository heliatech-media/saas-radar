"""
Configuration & Environment Settings for the Multi-Agent System.
"""

import os
import time
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
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Model Failover Pool: Auto-rotates if quota (429) or busy (503) occurs
AVAILABLE_AI_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-flash-latest",
    GEMINI_MODEL,
    "gemini-flash-lite-latest",
    "gemini-3.6-flash",
]

def call_gemini_with_failover(client, contents, config=None, preferred_model=None):
    models_to_try = []
    if preferred_model:
        models_to_try.append(preferred_model)
    for m in AVAILABLE_AI_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    last_error = None
    for model_name in models_to_try:
        try:
            kwargs = {"model": model_name, "contents": contents}
            if config:
                kwargs["config"] = config
            return client.models.generate_content(**kwargs)
        except Exception as e:
            err_str = str(e)
            last_error = e
            if any(k in err_str for k in ["429", "RESOURCEEXHAUSTED", "RESOURCE_EXHAUSTED", "503", "404", "UNAVAILABLE"]):
                print(f"[GeminiFailover] Notice: Model {model_name} busy/limited. Trying next model...")
                time.sleep(1.5)
                print(f"[GeminiFailover] Warning: Model {model_name} busy or exhausted. Auto-failing over to next model...")
                continue
            else:
                raise e
    raise last_error

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
    "apollo-io": "https://apollo.pxf.io/c/heliatech",
    "beehiiv": "https://www.beehiiv.com/?via=heliatech",
    "brevo": "https://brevo.partnerlinks.io/heliatech",
    "castmagic": "https://castmagic.io/?via=heliatech",
    "clickup": "https://clickup.pxf.io/c/heliatech",
    "cursor": "https://www.cursor.com/?via=heliatech",
    "getimg-ai": "https://getimg.ai/?via=heliatech",
    "heygen": "https://www.heygen.com/?via=heliatech",
    "linear": "https://linear.app/?via=heliatech",
    "lusha": "https://lusha.pxf.io/heliatech",
    "memberstack": "https://www.memberstack.com/?via=heliatech",
    "monday-com": "https://monday.com/?ref=heliatech",
    "framer": "https://framer.partnerstack.com/heliatech",
    "n8n": "https://n8n.io/?via=heliatech",
    "lemlist": "https://lemlist.com/?via=heliatech",
    "notion-ai": "https://affiliates.notion.so/heliatech",
    "opus-clip": "https://www.opus.pro/?via=heliatech",
    "partnerstack": "https://partnerstack.com/?via=heliatech",
    "phantombuster": "https://phantombuster.com/?via=heliatech",
    "podia": "https://www.podia.com/?via=heliatech",
    "printify": "https://printify.pxf.io/c/heliatech",
    "retool": "https://retool.com/?fpr=heliatech",
    "rewardful": "https://www.rewardful.com/?via=heliatech/?via=heliatech",
    "tweethunter": "https://tweethunter.io/?via=helia",
    "riverside-fm": "https://riverside.fm/?via=heliatech",
    "transistor-fm": "https://transistor.fm/?via=heliatech",
    "veed-io": "https://www.veed.io/?via=heliatech",
    "lovable": "https://lovable.dev/?via=heliatech",
    "supabase": "https://supabase.com",
    "typeform": "https://www.typeform.com",
    "vercel": "https://vercel.com/?via=heliatech",
    "jasper-ai": "https://partnerstack.com/jasper?via=heliatech",
    "voiceflow": "https://www.voiceflow.com",
    "wati": "https://www.wati.io/?fp_ref=heliatech",
    "webflow": "https://webflow.com",
    "zapier": "https://zapier.com/app/register?via=heliatech",
    "transistor": "https://transistor.fm/?via=heliatech",
    "podcastle": "https://podcastle.ai/?via=heliatech",
    "peripety": "https://try.elevenlabs.io/ajhd6t7k04dh",
    "resend": "https://resend.com/?via=heliatech",
    "riverside": "https://riverside.fm/?via=heliatech",
    "tally": "https://tally.so/?via=heliatech",
    "tome": "https://gamma.app",
    "veed": "https://www.veed.io/?via=heliatech",
    "klap": "https://klap.app/?via=heliatech",
    "v0": "https://v0.dev/?via=heliatech",
    "minicong": "https://minicong.ai/?via=heliatech",
    "dumpling-ai": "https://www.dumpling.ai/?via=heliatech",
    "julius-ai": "https://julius.ai/?via=heliatech",
    "sanity": "https://www.sanity.io/?ref=heliatech",
    "klaviyo": "https://partnerstack.com/klaviyo?via=heliatech",
    "kit": "https://kit.com/?via=heliatech",
    "screen-studio": "https://screen.studio/?via=heliatech",
    "descript": "https://descript.grsm.io/heliatech",
    "murf-ai": "https://murf.ai/?fp_ref=heliatech",
    "captions": "https://www.captions.ai/?via=heliatech"
}

# Strict Anonymity & Institutional Branding Policy:
# NEVER mention any personal names in any outgoing email, pitch, article, post, or document.
DEFAULT_BRAND_SIGNATURE = "The HeliaTech Partnerships Team"
DEFAULT_EDITORIAL_SIGNATURE = "The HeliaTech Editorial Team"
DEFAULT_EXECUTIVE_SENDER = "HeliaTech <partnership@heliatech.online>"
