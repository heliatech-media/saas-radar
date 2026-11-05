import json
import re
from pathlib import Path

path = Path("scripts/enrich_marketplace_catalog.py")
content = path.read_text(encoding="utf-8")

creator_data = {
    "SaaSGrowth Ops": {
        "slug": "saasgrowth-ops",
        "bio": "Consultant RevOps & Stripe Billing spécialisé dans l'éradication du churn involontaire et l'automatisation des relances dunning.",
        "website": "https://saasgrowth.example.com",
        "github": "saasgrowthops",
        "linkedin": "https://linkedin.com/company/saasgrowthops"
    },
    "RelationalHQ": {
        "slug": "relational-hq",
        "bio": "Architectes certifiés Airtable & Make.com concevant des operating systems complets pour agences et cabinets de conseil.",
        "website": "https://relationalhq.example.com",
        "github": "relationalhq",
        "linkedin": "https://linkedin.com/company/relationalhq"
    },
    "ContentEngine.ai": {
        "slug": "contentengine-ai",
        "bio": "Collectif d'ingénieurs en automatisation de contenu créant des pipelines IA pour transformer des vidéos en formats viraux multi-canaux.",
        "website": "https://contentengine.example.com",
        "github": "contentengine-ai",
        "linkedin": "https://linkedin.com/company/contentengine"
    },
    "SeniorStack Labs": {
        "slug": "seniorstack-labs",
        "bio": "Équipe de développeurs Full-Stack Next.js & Supabase concevant des règles strictes anti-hallucination pour Cursor et Copilot.",
        "website": "https://seniorstack.example.com",
        "github": "seniorstack",
        "linkedin": "https://linkedin.com/company/seniorstack"
    },
    "PipelinePioneers": {
        "slug": "pipeline-pioneers",
        "bio": "Partenaire Platinum HubSpot & Make.com automatisant les tunnels de vente, l'onboarding client et la synchronisation CRM.",
        "website": "https://pipelinepioneers.example.com",
        "github": "pipelinepioneers",
        "linkedin": "https://linkedin.com/company/pipelinepioneers"
    },
    "VoiceAgents Pro": {
        "slug": "voiceagents-pro",
        "bio": "Pionniers de la voix conversationnelle temps réel combinant ElevenLabs, Twilio et OpenAI pour l'accueil téléphonique autonome.",
        "website": "https://voiceagents.example.com",
        "github": "voiceagentspro",
        "linkedin": "https://linkedin.com/company/voiceagentspro"
    },
    "FintechOps Bureau": {
        "slug": "fintechops-bureau",
        "bio": "Cabinet d'ingénierie financière automatisant les rapprochements Stripe, QuickBooks et la conformité fiscale internationale.",
        "website": "https://fintechops.example.com",
        "github": "fintechops",
        "linkedin": "https://linkedin.com/company/fintechops"
    },
    "ChatOps Labs": {
        "slug": "chatops-labs",
        "bio": "Intégrateur officiel Meta WhatsApp Cloud API pour CRM conversationnels et qualification de leads ultra-rapide.",
        "website": "https://chatops.example.com",
        "github": "chatopslabs",
        "linkedin": "https://linkedin.com/company/chatopslabs"
    },
    "IntelScout Systems": {
        "slug": "intelscout-systems",
        "bio": "Spécialistes du web scraping headless, du monitoring tarifaire et de l'intelligence concurrentielle automatisée.",
        "website": "https://intelscout.example.com",
        "github": "intelscout",
        "linkedin": "https://linkedin.com/company/intelscout"
    },
    "VectorOps Academy": {
        "slug": "vectorops-academy",
        "bio": "Ingénieurs backend Python spécialisés dans LangChain v0.3+, FastAPI asynchrone et les bases vectorielles ChromaDB.",
        "website": "https://vectorops.example.com",
        "github": "vectorops",
        "linkedin": "https://linkedin.com/company/vectorops"
    },
    "RetentionLab": {
        "slug": "retentionlab",
        "bio": "Experts en Product-Led Growth et détection prédictive de désengagement client via télémétrie in-app.",
        "website": "https://retentionlab.example.com",
        "github": "retentionlab",
        "linkedin": "https://linkedin.com/company/retentionlab"
    }
}

for name, meta in creator_data.items():
    old_block = f'''        "creator": {{
            "name": "{name}",
            "badge": "([^"]+)",
            "avatar": "([^"]+)"
        }},'''
    new_block = f'''        "creator": {{
            "name": "{name}",
            "slug": "{meta['slug']}",
            "badge": "\\1",
            "avatar": "\\2",
            "bio": "{meta['bio']}",
            "website": "{meta['website']}",
            "github": "{meta['github']}",
            "linkedin": "{meta['linkedin']}"
        }},'''
    content = re.sub(old_block, new_block, content)

path.write_text(content, encoding="utf-8")
print("Updated scripts/enrich_marketplace_catalog.py with rich creator profiles.")
