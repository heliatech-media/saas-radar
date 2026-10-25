"""
Brand Marketing Campaign Publisher for HeliaTech Media.
Publishes dedicated high-converting brand campaigns (Calculator, Partner Portal, Deals Vault)
directly to LinkedIn and records telemetry in reports/brand_marketing_ledger.json.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from agents.linkedin_syndication_agent import LINKEDIN_API_URL

LEDGER_PATH = ROOT_DIR / "reports" / "brand_marketing_ledger.json"


def load_brand_ledger() -> dict:
    if LEDGER_PATH.exists():
        try:
            return json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"campaigns": [], "last_published": None}


def save_brand_ledger(data: dict):
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


CAMPAIGNS = {
    "calculator": {
        "title": "SaaS Waste & TCO Optimizer 2026 — HeliaTech Lab",
        "url": "https://heliatech.online/calculator",
        "thumbnail": "https://heliatech.online/images/blog/make.png",
        "text": """Pourquoi 95% des entreprises continuent de surpayer leur stack logicielle en 2026 ?

Au laboratoire HeliaTech, nous avons audité plus de 50 stacks B2B. Le constat empirique est sans appel :

1. Automatisation : Des équipes paient 599 $/mois pour Zapier alors que Make exécute les mêmes scénarios avec parsing JSON natif pour 29 $/mois.
2. Sales Intelligence : Des contrats ZoomInfo à 15 000 $/an sont renouvelés par inertie alors qu'Apollo.io propose 275M+ contacts vérifiés sans engagement annuel forcé.
3. Synthèse Vocale : Des API legacy facturent des surcoûts massifs alors qu'ElevenLabs v4 délivre une fidélité studio à sub-150ms.

Pour permettre à chaque fondateur, CTO et responsable d'opérations d'évaluer ses marges récupérables en toute transparence, nous mettons en accès libre notre simulateur :

⚡ Le Calculateur de TCO & Détecteur de Gaspillage SaaS 2026.

Ajustez vos volumes d'opérations et la taille de votre équipe pour calculer immédiatement votre capital récupérable :
👉 https://heliatech.online/calculator

#SaaS #B2B #TechProcurement #CloudArchitecture #Startups #CTO #Automation #HeliaTech"""
    },
    "partner": {
        "title": "HeliaTech B2B SaaS Partner Portal & Submission Registry",
        "url": "https://heliatech.online/partner",
        "thumbnail": "https://heliatech.online/badges/winner-2026-make.png",
        "text": """Fondateurs & CMOs de logiciels B2B : Faites certifier votre application dans le Radar HeliaTech 2026 🛰️

Notre observatoire technologique autonome évalue et benchmarke en continu les architectures logicielles les plus performantes du marché (Make, Supabase, ElevenLabs, Apollo...).

Nous ouvrons officiellement notre portail de soumission pour les éditeurs SaaS :

✓ Accréditation officielle & badge vectoriel SVG pour votre landing page
✓ Fiche détaillée et exposition auprès de 100 000+ décideurs tech qualifiés
✓ Ingestion dans notre Vault d'offres exclusives (/deals)
✓ Possibilité d'audit accéléré en 48 heures

Vous offrez un outil performant et un avantage exclusif à notre communauté ?
Soumettez votre logiciel dès aujourd'hui :
👉 https://heliatech.online/partner

#SaaS #Startups #ProductManagement #Founders #TechNews #Affiliation #Rewardful #HeliaTech"""
    },
    "blueprint": {
        "title": "The 2026 Tech Stack Blueprint — Zero-Waste Software Architecture",
        "url": "https://heliatech.online/blueprint",
        "thumbnail": "https://heliatech.online/images/blog/make.png",
        "text": """En 2026, une équipe de 3 personnes peut générer la valeur d'une entreprise de 50 salariés grâce aux architectures logicielles de nouvelle génération.

Au sein de l'Observatoire HeliaTech, nous dévoilons aujourd'hui notre Blueprint d'Architecture 2026 :

🚀 Un guide interactif et gratuit pour composer votre stack logicielle sur-mesure (Solopreneur, Agence B2B, Startup, Média) et éliminer jusqu'à 65% de dépenses superflues.

Ce que révèle notre benchmark :
• Comment orchestrer des flux événementiels avec Make & n8n pour 1/5ème du coût de Zapier
• Pourquoi enrichir 275M+ profils avec Apollo.io surpasse les contrats rigides à 15k$/an
• Comment industrialiser la voix studio et la vidéo IA avec ElevenLabs & HeyGen
• Pourquoi migrer sur Supabase & Vercel garantit une latence sub-100ms mondiale

Configurez votre architecture et découvrez vos gains de trésorerie nets :
👉 https://heliatech.online/blueprint

#SoftwareArchitecture #SaaS #AI #CTO #Founders #Automation #TechLead #HeliaTech"""
    }
}


def publish_campaign(campaign_name: str = "calculator") -> dict:
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    author_urn = os.getenv("LINKEDIN_AUTHOR_URN", "")
    enabled = os.getenv("LINKEDIN_BROADCAST_ENABLED", "false").lower() == "true"

    if not enabled:
        print("[Brand Marketing] 🔒 LINKEDIN_BROADCAST_ENABLED is false. Broadcast aborted.")
        return {"status": "STANDBY"}

    if not token or not author_urn:
        print("[Brand Marketing] ❌ Missing LinkedIn credentials.")
        return {"status": "ERROR", "reason": "missing_credentials"}

    camp = CAMPAIGNS.get(campaign_name)
    if not camp:
        print(f"[Brand Marketing] ❌ Unknown campaign: {campaign_name}")
        return {"status": "ERROR", "reason": "unknown_campaign"}

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }

    media_item = {
        "status": "READY",
        "originalUrl": camp["url"],
        "title": {"text": camp["title"][:200]}
    }
    if camp.get("thumbnail"):
        media_item["thumbnails"] = [{"url": camp["thumbnail"]}]

    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": camp["text"]
                },
                "shareMediaCategory": "ARTICLE",
                "media": [media_item]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    print(f"[Brand Marketing] 🚀 Broadcasting campaign '{campaign_name}' to LinkedIn...")
    res = requests.post(LINKEDIN_API_URL, json=payload, headers=headers, timeout=20)
    if res.status_code in [200, 201]:
        data = res.json()
        share_urn = data.get("id")
        print(f"[Brand Marketing] ✅ SUCCESS! Campaign '{campaign_name}' published to LinkedIn!")
        print(f"                  Share URN: {share_urn}")

        ledger = load_brand_ledger()
        ledger["campaigns"].append({
            "name": campaign_name,
            "published_at": datetime.now().isoformat(),
            "share_urn": share_urn,
            "url": camp["url"]
        })
        ledger["last_published"] = datetime.now().isoformat()
        save_brand_ledger(ledger)

        return {"status": "SUCCESS", "campaign": campaign_name, "share_urn": share_urn}
    else:
        print(f"[Brand Marketing] ⚠️ Error broadcasting: {res.status_code} - {res.text}")
        return {"status": "API_ERROR", "code": res.status_code, "detail": res.text}


if __name__ == "__main__":
    camp_arg = sys.argv[1] if len(sys.argv) > 1 else "calculator"
    result = publish_campaign(camp_arg)
    print(f"\nResult: {json.dumps(result, indent=2)}")
