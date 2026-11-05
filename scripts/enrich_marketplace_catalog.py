"""
Enriches the HeliaTech Automation Marketplace catalog with 12 flagship blueprints,
including visual pipeline nodes, interactive FAQs, customer reviews, and sanitized code snippets.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TEMPLATES = [
    {
        "id": "tpl_n8n_ai_lead_enricher",
        "slug": "n8n-ai-lead-enricher-waterfall",
        "title": "n8n AI Waterfall Lead Enrichment & Scoring Engine",
        "tagline": "Turn cold domain names into fully enriched CEO dossiers using Claude 3.5 & LinkedIn Scraping.",
        "ecosystem": "n8n",
        "category": "Lead Gen & Sales",
        "price_usd": 49,
        "price_cents": 4900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "AutomateScale Studio",
            "slug": "automatescale-studio",
            "badge": "Verified Pro Agency",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=AutomateScale",
            "bio": "Studio d'ingénierie spécialisé dans les architectures n8n haute-performance et l'enrichissement de données B2B sans abonnement SaaS tiers.",
            "website": "https://automatescale.example.com",
            "github": "automatescale",
            "linkedin": "https://linkedin.com/company/automatescale"
        },
        "nodes_count": 18,
        "estimated_hours_saved": 24,
        "monthly_savings_estimate": "$450 / mo vs Clay",
        "required_services": ["OpenAI / Anthropic", "Proxycurl / BrightData", "Airtable / Postgres"],
        "highlights": [
            "Bypasses expensive Clay credits via direct API waterfall",
            "Extracts verified emails with zero bounce rates",
            "Scores ICP fitness automatically using Claude 3.5 Sonnet",
            "Push ready-to-contact leads directly into Instantly / Smartlead"
        ],
        "sales_count": 142,
        "rating": 4.95,
        "reviews_count": 28,
        "is_featured": True,
        "pipeline_steps": [
            {"step": 1, "name": "Webhook Inbound Lead", "type": "Trigger", "icon": "⚡", "desc": "Capture les domaines ou emails depuis vos formulaires sans latence"},
            {"step": 2, "name": "Claude 3.5 ICP Scorer", "type": "AI Engine", "icon": "🤖", "desc": "Scrape le site web et analyse l'adéquation au client idéal"},
            {"step": 3, "name": "Waterfall Decision Router", "type": "Router", "icon": "🔀", "desc": "Bascule entre Apollo, Hunter et Dropcontact pour zéro bounce"},
            {"step": 4, "name": "Airtable CRM Sync", "type": "Database", "icon": "📊", "desc": "Enregistre la fiche enrichie avec métadonnées financières"},
            {"step": 5, "name": "Slack High-Priority Alert", "type": "Notify", "icon": "🔔", "desc": "Notifie les commerciaux si le score ICP dépasse 85/100"}
        ],
        "faq": [
            {"q": "Combien de temps faut-il pour déployer ce blueprint ?", "a": "Moins de 5 minutes. Importez le fichier .json dans n8n, renseignez vos clés API et activez le webhook d'entrée."},
            {"q": "Quels sont les coûts d'exécution API estimés ?", "a": "Environ $0.003 par lead traité grâce à l'optimisation des prompts et au routage direct sans intermédiaire."},
            {"q": "Puis-je modifier ou étendre ce workflow ?", "a": "Absolument. La licence commerciale illimitée vous donne 100% de liberté pour ajouter ou retirer des nœuds."}
        ],
        "reviews": [
            {"author": "Marc L.", "role": "Head of Growth, B2B SaaS", "rating": 5, "date": "Il y a 3 jours", "comment": "Déployé en 10 minutes dans notre n8n cloud. Nous avons économisé plus de 450$/mois sur nos abonnements d'enrichissement."},
            {"author": "Sarah D.", "role": "RevOps Architect", "rating": 5, "date": "Il y a 1 semaine", "comment": "La gestion des erreurs est remarquable. Rien ne tombe en timeout. Code d'ingénierie irréprochable."}
        ],
        "json_snippet": "{\n  \"name\": \"n8n AI Lead Enrichment Waterfall\",\n  \"nodes\": [\n    {\n      \"parameters\": { \"path\": \"inbound-lead\", \"responseMode\": \"onReceived\" },\n      \"name\": \"Webhook Inbound Lead\",\n      \"type\": \"n8n-nodes-base.webhook\",\n      \"typeVersion\": 1\n    },\n    {\n      \"parameters\": {\n        \"model\": \"claude-3-5-sonnet-20241022\",\n        \"prompt\": \"Evaluate lead company: {{$json.domain}}\"\n      },\n      \"name\": \"Claude 3.5 ICP Scorer\",\n      \"type\": \"n8n-nodes-base.anthropic\"\n    }\n  ]\n}"
    },
    {
        "id": "tpl_make_saas_churn_preventer",
        "slug": "make-stripe-churn-rescue-blueprint",
        "title": "Make.com Stripe Failed Payment & Churn Recovery Machine",
        "tagline": "Recover up to 48% of failed credit card subscriptions with smart multi-channel dunning.",
        "ecosystem": "make",
        "category": "Fintech & RevOps",
        "price_usd": 39,
        "price_cents": 3900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "SaaSGrowth Ops",
            "slug": "saasgrowth-ops",
            "badge": "Verified Engineer",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=SaaSOps",
            "bio": "Consultant RevOps & Stripe Billing spécialisé dans l'éradication du churn involontaire et l'automatisation des relances dunning.",
            "website": "https://saasgrowth.example.com",
            "github": "saasgrowthops",
            "linkedin": "https://linkedin.com/company/saasgrowthops"
        },
        "nodes_count": 14,
        "estimated_hours_saved": 16,
        "monthly_savings_estimate": "$1,200 / mo recovered MRR",
        "required_services": ["Stripe Webhooks", "Resend / Brevo", "Slack Alerting"],
        "highlights": [
            "Catches invoice.payment_failed instantly with zero latency",
            "Smart fallback emails with 1-click update billing portal links",
            "Internal Slack escalation for accounts > $250/mo",
            "Full idempotency key handling to prevent double-charging"
        ],
        "sales_count": 89,
        "rating": 5.0,
        "reviews_count": 19,
        "is_featured": True,
        "pipeline_steps": [
            {"step": 1, "name": "Stripe Webhook Listener", "type": "Trigger", "icon": "💳", "desc": "Capture invoice.payment_failed et customer.subscription.updated"},
            {"step": 2, "name": "Smart Dunning Logic", "type": "Router", "icon": "⚙️", "desc": "Calcule le palier d'impayé (J+1, J+3, J+7) et l'historique client"},
            {"step": 3, "name": "Resend Transactional Email", "type": "Email", "icon": "✉️", "desc": "Envoie un email personnalisé avec lien direct Stripe Customer Portal"},
            {"step": 4, "name": "Executive Slack Channel", "type": "Notify", "icon": "🚨", "desc": "Alerte immédiate pour les comptes VIP en risque de churn"}
        ],
        "faq": [
            {"q": "Ce blueprint fonctionne-t-il avec Stripe Billing existant ?", "a": "Oui, il s'intègre en parallèle sans perturber vos relances Stripe automatiques."},
            {"q": "Les emails envoyés sont-ils personnalisables ?", "a": "Totalement, les modèles HTML Resend et texte brut sont fournis et prêts à adapter à votre charte."}
        ],
        "reviews": [
            {"author": "Julien M.", "role": "CEO, Micro-SaaS", "rating": 5, "date": "Il y a 5 jours", "comment": "Ce blueprint nous a fait récupérer 3 clients à 99$/mois dès sa première semaine d'activation. Rentabilisé en 24h."}
        ],
        "json_snippet": "{\n  \"name\": \"Stripe Churn Recovery Machine\",\n  \"blueprint\": {\n    \"flow\": [\n      { \"id\": 1, \"module\": \"stripe:WatchEvents\" },\n      { \"id\": 2, \"module\": \"resend:SendEmail\" },\n      { \"id\": 3, \"module\": \"slack:CreateMessage\" }\n    ]\n  }\n}"
    },
    {
        "id": "tpl_airtable_client_portal_os",
        "slug": "airtable-b2b-client-portal-os",
        "title": "Airtable Enterprise Agency OS & Auto-Invoicing Schema",
        "tagline": "Complete relational agency operating system with automated milestone billing and task approvals.",
        "ecosystem": "airtable",
        "category": "Agency Operations",
        "price_usd": 29,
        "price_cents": 2900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "RelationalHQ",
            "slug": "relational-hq",
            "badge": "Airtable Certified Architect",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=RelationalHQ",
            "bio": "Architectes certifiés Airtable & Make.com concevant des operating systems complets pour agences et cabinets de conseil.",
            "website": "https://relationalhq.example.com",
            "github": "relationalhq",
            "linkedin": "https://linkedin.com/company/relationalhq"
        },
        "nodes_count": 8,
        "estimated_hours_saved": 35,
        "monthly_savings_estimate": "Replaces $120/mo ClickUp + Toggl setup",
        "required_services": ["Airtable Pro", "Make.com (optional)", "Stripe Invoicing"],
        "highlights": [
            "Clean normalized relational structure: Clients, Deliverables, Invoices, Hours",
            "Automated contract generation when deal moves to Won",
            "Client-facing portal views with restricted read-only permissions",
            "Real-time agency margin and consultant utilization dashboards"
        ],
        "sales_count": 67,
        "rating": 4.9,
        "reviews_count": 14,
        "is_featured": False,
        "pipeline_steps": [
            {"step": 1, "name": "CRM Deal Won Trigger", "type": "Trigger", "icon": "🤝", "desc": "Active le projet dès signature électronique du contrat"},
            {"step": 2, "name": "Project Workspace Provisioning", "type": "Automation", "icon": "📂", "desc": "Crée l'arbre de livrables et jalons pré-configurés"},
            {"step": 3, "name": "Client Portal Interface", "type": "UI View", "icon": "💻", "desc": "Accès client sécurisé pour validation des jalons"},
            {"step": 4, "name": "Automated Milestone Billing", "type": "Fintech", "icon": "🧾", "desc": "Génère la facture Stripe dès approbation d'une étape"}
        ],
        "faq": [
            {"q": "Ce schéma est-il compatible avec le plan gratuit d'Airtable ?", "a": "Oui, les formules et relations fonctionnent sur le plan Free, mais le plan Team/Business débloque les extensions avancées."}
        ],
        "reviews": [
            {"author": "Thierry B.", "role": "Fondateur Agence Web", "rating": 5, "date": "Il y a 2 semaines", "comment": "Clarté mathématique. Plus besoin de jongler entre Notion et un outil de devis."}
        ],
        "json_snippet": "{\n  \"schema\": \"Airtable Enterprise Agency OS\",\n  \"tables\": [\"Clients\", \"Projects\", \"Deliverables\", \"Invoices\", \"TimeLogs\"],\n  \"views\": [\"Client Portal View\", \"Executive Margin Dashboard\"]\n}"
    },
    {
        "id": "tpl_n8n_youtube_to_linkedin_carousel",
        "slug": "n8n-youtube-to-linkedin-carousels",
        "title": "n8n YouTube Video to Viral LinkedIn Carousel Generator",
        "tagline": "Transcribe any long video, extract punchy takeaways, and format multi-slide PDF carousels via Puppeteer.",
        "ecosystem": "n8n",
        "category": "Social & Content",
        "price_usd": 35,
        "price_cents": 3500,
        "platform_fee_percent": 20,
        "creator": {
            "name": "ContentEngine.ai",
            "slug": "contentengine-ai",
            "badge": "Automation Lead",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=ContentEngine",
            "bio": "Collectif d'ingénieurs en automatisation de contenu créant des pipelines IA pour transformer des vidéos en formats viraux multi-canaux.",
            "website": "https://contentengine.example.com",
            "github": "contentengine-ai",
            "linkedin": "https://linkedin.com/company/contentengine"
        },
        "nodes_count": 22,
        "estimated_hours_saved": 18,
        "monthly_savings_estimate": "$290 / mo vs Copy.ai & Canva Teams",
        "required_services": ["OpenAI Whisper", "Anthropic Claude 3.5", "Puppeteer Node / HTML Render"],
        "highlights": [
            "Whisper speech-to-text with auto speaker-diarization",
            "Claude 3.5 prompts tuned for viral LinkedIn readability",
            "Auto-generates 1080x1350 PDF carousel slides via HTML templates",
            "Direct post scheduling via Buffer or LinkedIn API"
        ],
        "sales_count": 115,
        "rating": 4.88,
        "reviews_count": 22,
        "is_featured": True,
        "pipeline_steps": [
            {"step": 1, "name": "YouTube URL Webhook", "type": "Trigger", "icon": "🎥", "desc": "Réception du lien vidéo à transcrire"},
            {"step": 2, "name": "Whisper Audio Extraction", "type": "AI Engine", "icon": "🎙️", "desc": "Transcription intégrale haute-fidélité"},
            {"step": 3, "name": "Viral Hook Synthesizer", "type": "AI Prompt", "icon": "✍️", "desc": "Claude 3.5 découpe le contenu en 6 slides percutantes"},
            {"step": 4, "name": "Puppeteer PDF Renderer", "type": "Render", "icon": "📄", "desc": "Compilation en carrousel PDF 1080x1350"},
            {"step": 5, "name": "LinkedIn Scheduler", "type": "Publish", "icon": "🚀", "desc": "Programmation automatique sur votre compte"}
        ],
        "faq": [
            {"q": "Les polices et couleurs des slides sont-elles personnalisables ?", "a": "Oui, le nœud HTML contient du code Tailwind simple pour adapter votre logo et vos couleurs."}
        ],
        "reviews": [
            {"author": "David K.", "role": "Tech Influencer", "rating": 5, "date": "Il y a 4 jours", "comment": "Nos carrousels LinkedIn ont fait +180% d'engagement sans y passer 3 heures par jour."}
        ],
        "json_snippet": "{\n  \"name\": \"YouTube to LinkedIn Carousel Engine\",\n  \"nodes\": [\n    { \"name\": \"Download Audio\", \"type\": \"n8n-nodes-base.httpRequest\" },\n    { \"name\": \"Whisper Transcribe\", \"type\": \"n8n-nodes-base.openAi\" },\n    { \"name\": \"Puppeteer PDF Builder\", \"type\": \"n8n-nodes-base.puppeteer\" }\n  ]\n}"
    },
    {
        "id": "tpl_cursor_rules_nextjs_supabase",
        "slug": "cursor-rules-nextjs-tailwind-supabase-masterpack",
        "title": "Cursor AI Rules: Next.js 15, Tailwind & Supabase Masterpack",
        "tagline": "Turn Cursor into a Senior Full-Stack Engineer with deterministic rules and strict anti-hallucination guards.",
        "ecosystem": "cursor",
        "category": "AI Developer Tools",
        "price_usd": 19,
        "price_cents": 1900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "SeniorStack Labs",
            "slug": "seniorstack-labs",
            "badge": "Principal Architect",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=SeniorStack",
            "bio": "Équipe de développeurs Full-Stack Next.js & Supabase concevant des règles strictes anti-hallucination pour Cursor et Copilot.",
            "website": "https://seniorstack.example.com",
            "github": "seniorstack",
            "linkedin": "https://linkedin.com/company/seniorstack"
        },
        "nodes_count": 6,
        "estimated_hours_saved": 40,
        "monthly_savings_estimate": "Cuts 60% of prompt debugging iterations",
        "required_services": ["Cursor IDE", "Next.js 15 App Router", "Supabase Client"],
        "highlights": [
            "Forces strict TypeScript types, bans 'any' completely",
            "Enforces Server Actions and Row-Level Security best practices",
            "Prevents CSS regressions with strict Tailwind design tokens",
            "Includes dedicated migration and edge function guidelines"
        ],
        "sales_count": 210,
        "rating": 5.0,
        "reviews_count": 45,
        "is_featured": True,
        "pipeline_steps": [
            {"step": 1, "name": "Global .cursorrules Parser", "type": "IDE Guard", "icon": "🤖", "desc": "Intercepte chaque commande Cursor Agent"},
            {"step": 2, "name": "TypeScript Type Enforcer", "type": "Compiler Guard", "icon": "🛡️", "desc": "Interdit tout 'any' et exige des types stricts Zod"},
            {"step": 3, "name": "Supabase RLS Validator", "type": "Database Guard", "icon": "🔒", "desc": "Valide l'isolation multi-tenant avant écriture"},
            {"step": 4, "name": "Tailwind Token Lock", "type": "UI Guard", "icon": "🎨", "desc": "Garantit la conformité dark-mode sans conflits CSS"}
        ],
        "faq": [
            {"q": "Comment installer ce pack ?", "a": "Copiez simplement le fichier .cursorrules à la racine de votre projet Git. Cursor le détecte immédiatement."}
        ],
        "reviews": [
            {"author": "Guillaume R.", "role": "Senior Frontend Dev", "rating": 5, "date": "Il y a 6 jours", "comment": "Cursor ne part plus en boucle hallucinée. Le code généré passe les linters du premier coup."}
        ],
        "json_snippet": "{\n  \"rules\": [\n    \"Always use strict TypeScript. Never use any.\",\n    \"Use Next.js 15 App Router conventions and Server Actions.\",\n    \"Enforce Supabase RLS security policies on all database mutations.\"\n  ]\n}"
    },
    {
        "id": "tpl_make_hubspot_onboarding",
        "slug": "make-hubspot-deal-won-celebration-and-onboarding",
        "title": "Make.com HubSpot Deal Won & Client Onboarding Sequence",
        "tagline": "Automate contract creation, Slack celebrations, Google Drive folders, and Notion client dashboards.",
        "ecosystem": "make",
        "category": "CRM & Sales",
        "price_usd": 25,
        "price_cents": 2500,
        "platform_fee_percent": 20,
        "creator": {
            "name": "PipelinePioneers",
            "slug": "pipeline-pioneers",
            "badge": "HubSpot Platinum Partner",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=PipelinePioneers",
            "bio": "Partenaire Platinum HubSpot & Make.com automatisant les tunnels de vente, l'onboarding client et la synchronisation CRM.",
            "website": "https://pipelinepioneers.example.com",
            "github": "pipelinepioneers",
            "linkedin": "https://linkedin.com/company/pipelinepioneers"
        },
        "nodes_count": 12,
        "estimated_hours_saved": 14,
        "monthly_savings_estimate": "$350 / mo in saved manual account manager time",
        "required_services": ["HubSpot CRM", "Google Drive", "Slack", "Notion API"],
        "highlights": [
            "Triggers instantly on deal stage: 'Closed Won'",
            "Creates structured client drive folders with template deliverables",
            "Provisions customer Notion portal from master blueprint",
            "Posts custom win gifs and MRR breakdown in team Slack"
        ],
        "sales_count": 52,
        "rating": 4.85,
        "reviews_count": 11,
        "is_featured": False,
        "pipeline_steps": [
            {"step": 1, "name": "HubSpot Closed Won Hook", "type": "Trigger", "icon": "🎯", "desc": "Déclenchement instantané dès signature commerciale"},
            {"step": 2, "name": "Google Drive Folder Tree", "type": "Storage", "icon": "📁", "desc": "Crée l'arborescence client sécurisée avec modèles de documents"},
            {"step": 3, "name": "Notion Client Portal Duplicate", "type": "Workspace", "icon": "📝", "desc": "Clone l'espace de suivi et partage les droits en lecture"},
            {"step": 4, "name": "Slack Team Celebration", "type": "Notify", "icon": "🎉", "desc": "Diffuse l'annonce avec le MRR signé et félicitations"}
        ],
        "faq": [
            {"q": "Fonctionne-t-il avec HubSpot Starter ?", "a": "Oui, les webhooks standards ou les triggers polling Make.com sont pris en charge."}
        ],
        "reviews": [
            {"author": "Céline P.", "role": "Directrice Commerciale", "rating": 5, "date": "Il y a 1 semaine", "comment": "Nos nouveaux clients reçoivent leur espace d'onboarding en 2 minutes au lieu d'une demi-journée."}
        ],
        "json_snippet": "{\n  \"name\": \"HubSpot Deal Won & Onboarding Sequence\",\n  \"blueprint\": {\n    \"flow\": [\n      { \"id\": 1, \"module\": \"hubspot:WatchDeals\" },\n      { \"id\": 2, \"module\": \"google-drive:CreateFolder\" },\n      { \"id\": 3, \"module\": \"notion:DuplicatePage\" }\n    ]\n  }\n}"
    },
    # --- 6 NOUVEAUX BLUEPRINTS ELITE AJOUTÉS ---
    {
        "id": "tpl_n8n_ai_voice_receptionist",
        "slug": "n8n-ai-voice-receptionist-elevenlabs",
        "title": "n8n Autonomous AI Voice Receptionist & Call Routing",
        "tagline": "Answers phone calls 24/7 with human-grade ElevenLabs voice, qualifies leads, and books Calendly meetings.",
        "ecosystem": "n8n",
        "category": "Customer Support",
        "price_usd": 69,
        "price_cents": 6900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "VoiceAgents Pro",
            "slug": "voiceagents-pro",
            "badge": "AI Voice Specialist",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=VoiceAgents",
            "bio": "Pionniers de la voix conversationnelle temps réel combinant ElevenLabs, Twilio et OpenAI pour l'accueil téléphonique autonome.",
            "website": "https://voiceagents.example.com",
            "github": "voiceagentspro",
            "linkedin": "https://linkedin.com/company/voiceagentspro"
        },
        "nodes_count": 26,
        "estimated_hours_saved": 45,
        "monthly_savings_estimate": "$1,800 / mo vs Human Call Center",
        "required_services": ["Twilio / SIP", "ElevenLabs Conversational AI", "OpenAI GPT-4o", "Calendly API"],
        "highlights": [
            "Sub-500ms voice response latency using ElevenLabs Flash model",
            "Natural human interruption handling & noise suppression",
            "Checks team availability and sends calendar invites during call",
            "Transcribes call and posts summary & audio recording to CRM"
        ],
        "sales_count": 78,
        "rating": 4.96,
        "reviews_count": 16,
        "is_featured": True,
        "pipeline_steps": [
            {"step": 1, "name": "Twilio Inbound Call Hook", "type": "Trigger", "icon": "📞", "desc": "Décroche l'appel entrant sans latence"},
            {"step": 2, "name": "ElevenLabs Voice Stream", "type": "Audio Engine", "icon": "🎙️", "desc": "Conversation vocale fluide en français et anglais"},
            {"step": 3, "name": "GPT-4o Intent Classifier", "type": "AI Engine", "icon": "🧠", "desc": "Qualifie le besoin client et extrait les coordonnées"},
            {"step": 4, "name": "Calendly Instant Booking", "type": "Calendar", "icon": "📅", "desc": "Fixe le rendez-vous commercial directement en ligne"},
            {"step": 5, "name": "CRM Audio & Transcript Log", "type": "Database", "icon": "📋", "desc": "Archive l'enregistrement et le compte-rendu dans le CRM"}
        ],
        "faq": [
            {"q": "La voix sonne-t-elle comme un robot ?", "a": "Non, le modèle ElevenLabs reproduit les inflexions naturelles, les respirations et la modulation émotionnelle d'un humain."},
            {"q": "Quel numéro de téléphone peut-on utiliser ?", "a": "N'importe quel numéro fixe ou mobile provisionné via Twilio en quelques clics."}
        ],
        "reviews": [
            {"author": "Karim T.", "role": "CEO, Agence Immobilière", "rating": 5, "date": "Il y a 2 jours", "comment": "Nous ne perdons plus aucun appel le week-end ou en soirée. 8 rendez-vous bookés automatiquement la première semaine."}
        ],
        "json_snippet": "{\n  \"name\": \"Autonomous AI Voice Receptionist\",\n  \"nodes\": [\n    { \"name\": \"Twilio Voice Webhook\", \"type\": \"n8n-nodes-base.webhook\" },\n    { \"name\": \"ElevenLabs Stream\", \"type\": \"n8n-nodes-base.httpRequest\" },\n    { \"name\": \"Calendly Booking\", \"type\": \"n8n-nodes-base.calendly\" }\n  ]\n}"
    },
    {
        "id": "tpl_make_quickbooks_invoicing",
        "slug": "make-stripe-quickbooks-automated-invoicing",
        "title": "Make.com Stripe & Stripe Tax to QuickBooks Live Sync",
        "tagline": "Zero manual accounting: syncs charges, refunds, Stripe fees and VAT automatically to QuickBooks.",
        "ecosystem": "make",
        "category": "Fintech & RevOps",
        "price_usd": 49,
        "price_cents": 4900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "FintechOps Bureau",
            "slug": "fintechops-bureau",
            "badge": "Certified CPA Automator",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=FintechOps",
            "bio": "Cabinet d'ingénierie financière automatisant les rapprochements Stripe, QuickBooks et la conformité fiscale internationale.",
            "website": "https://fintechops.example.com",
            "github": "fintechops",
            "linkedin": "https://linkedin.com/company/fintechops"
        },
        "nodes_count": 16,
        "estimated_hours_saved": 20,
        "monthly_savings_estimate": "$300 / mo in CPA bookkeeping fees",
        "required_services": ["Stripe Webhooks", "QuickBooks Online API", "Slack Alerts"],
        "highlights": [
            "Reconciles Stripe processing fees in separate expense accounts",
            "Handles multi-currency conversions and tax jurisdictions",
            "Auto-matches customer email to avoid duplicate customer records",
            "Zero reconciliation errors during month-end closing"
        ],
        "sales_count": 94,
        "rating": 4.92,
        "reviews_count": 21,
        "is_featured": False,
        "pipeline_steps": [
            {"step": 1, "name": "Stripe Charge Succeeded Hook", "type": "Trigger", "icon": "💳", "desc": "Capture chaque encaissement avec TVA et devise"},
            {"step": 2, "name": "Customer Duplicate Check", "type": "Logic", "icon": "🔍", "desc": "Retrouve ou crée le compte client dans QuickBooks"},
            {"step": 3, "name": "QuickBooks Sales Receipt Sync", "type": "Accounting", "icon": "📑", "desc": "Génère l'écriture comptable avec autoliquidation si applicable"},
            {"step": 4, "name": "Stripe Fee Separation Node", "type": "Expense", "icon": "📉", "desc": "Isole les frais Stripe dans le compte de charges adéquat"}
        ],
        "faq": [
            {"q": "Gère-t-il les remboursements partiels ?", "a": "Oui, le nœud charge.refunded crée un avoir (Credit Memo) correspondant dans QuickBooks."}
        ],
        "reviews": [
            {"author": "Nicolas F.", "role": "DAF Partagé", "rating": 5, "date": "Il y a 5 jours", "comment": "Plus aucune erreur de centimes lors de la clôture mensuelle. Le rêve de tout comptable."}
        ],
        "json_snippet": "{\n  \"name\": \"Stripe to QuickBooks Live Sync\",\n  \"blueprint\": {\n    \"flow\": [\n      { \"id\": 1, \"module\": \"stripe:WatchCharges\" },\n      { \"id\": 2, \"module\": \"quickbooks:CreateSalesReceipt\" }\n    ]\n  }\n}"
    },
    {
        "id": "tpl_airtable_whatsapp_crm",
        "slug": "airtable-whatsapp-cloud-api-nurturing-crm",
        "title": "Airtable + WhatsApp Cloud API Multi-Agent Nurturing CRM",
        "tagline": "Two-way WhatsApp messaging CRM inside Airtable with 98% open rates and automated AI follow-ups.",
        "ecosystem": "airtable",
        "category": "CRM & Sales",
        "price_usd": 39,
        "price_cents": 3900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "ChatOps Labs",
            "slug": "chatops-labs",
            "badge": "Meta Tech Provider",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=ChatOps",
            "bio": "Intégrateur officiel Meta WhatsApp Cloud API pour CRM conversationnels et qualification de leads ultra-rapide.",
            "website": "https://chatops.example.com",
            "github": "chatopslabs",
            "linkedin": "https://linkedin.com/company/chatopslabs"
        },
        "nodes_count": 10,
        "estimated_hours_saved": 28,
        "monthly_savings_estimate": "Replaces $180/mo WATI / ManyChat subscription",
        "required_services": ["Airtable Pro", "Meta WhatsApp Business Cloud API", "Make / Webhook"],
        "highlights": [
            "Official WhatsApp Cloud API integration with zero third-party markups",
            "Live chat interface built natively into Airtable Interfaces",
            "Auto-triggers follow-up sequences based on customer tags",
            "GPT-4o auto-replies when human agents are offline"
        ],
        "sales_count": 82,
        "rating": 4.94,
        "reviews_count": 17,
        "is_featured": True,
        "pipeline_steps": [
            {"step": 1, "name": "WhatsApp Inbound Message", "type": "Trigger", "icon": "💬", "desc": "Webhook officiel Meta Cloud API direct"},
            {"step": 2, "name": "Airtable Thread Matcher", "type": "Database", "icon": "📂", "desc": "Rattache le message à la fiche prospect existante"},
            {"step": 3, "name": "AI Auto-Response Engine", "type": "AI Engine", "icon": "🤖", "desc": "Répond instantanément aux questions fréquentes si hors-ligne"},
            {"step": 4, "name": "Outbound WhatsApp Dispatcher", "type": "Messaging", "icon": "📤", "desc": "Envoie les relances et devis directement sur WhatsApp"}
        ],
        "faq": [
            {"q": "Ai-je besoin d'un compte Meta Business vérifié ?", "a": "Oui, pour l'API officielle WhatsApp Cloud. Le tutoriel pas-à-pas d'approbation est inclus."}
        ],
        "reviews": [
            {"author": "Romain V.", "role": "Fondateur E-commerce B2B", "rating": 5, "date": "Il y a 1 semaine", "comment": "Taux d'ouverture de 95% par rapport à 20% par email. Nos prospects répondent dans les 5 minutes."}
        ],
        "json_snippet": "{\n  \"schema\": \"Airtable WhatsApp CRM\",\n  \"tables\": [\"Conversations\", \"Messages\", \"Templates\", \"Contacts\"],\n  \"automations\": [\"Meta Webhook Receiver\", \"AI Auto-Reply\", \"Dunning Followup\"]\n}"
    },
    {
        "id": "tpl_n8n_competitor_radar",
        "slug": "n8n-multi-agent-competitor-intelligence-radar",
        "title": "n8n Multi-Agent Competitor Pricing & Feature Watcher",
        "tagline": "Autonomous web scraper monitoring competitor pricing changes, job posts, and release notes weekly.",
        "ecosystem": "n8n",
        "category": "Lead Gen & Sales",
        "price_usd": 59,
        "price_cents": 5900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "IntelScout Systems",
            "slug": "intelscout-systems",
            "badge": "Data Scraping Specialist",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=IntelScout",
            "bio": "Spécialistes du web scraping headless, du monitoring tarifaire et de l'intelligence concurrentielle automatisée.",
            "website": "https://intelscout.example.com",
            "github": "intelscout",
            "linkedin": "https://linkedin.com/company/intelscout"
        },
        "nodes_count": 24,
        "estimated_hours_saved": 32,
        "monthly_savings_estimate": "$600 / mo vs Crayon / Klue",
        "required_services": ["Firecrawl / Browserless", "Claude 3.5 Sonnet", "Notion / Slack"],
        "highlights": [
            "Scrapes complex SPA pricing tables with headless Chromium",
            "Detects silent price hikes or feature tier repackaging",
            "Monitors competitor careers page to predict upcoming product launches",
            "Synthesizes weekly executive executive intelligence brief in Notion"
        ],
        "sales_count": 64,
        "rating": 4.97,
        "reviews_count": 13,
        "is_featured": False,
        "pipeline_steps": [
            {"step": 1, "name": "Weekly Cron Scheduler", "type": "Trigger", "icon": "⏰", "desc": "Déclenche l'inspection chaque lundi à 6h00"},
            {"step": 2, "name": "Headless Browser Scraper", "type": "Scraper", "icon": "🕷️", "desc": "Capture le HTML et captures d'écran des concurrents"},
            {"step": 3, "name": "Visual Diff & Text AI Analyzer", "type": "AI Engine", "icon": "🔍", "desc": "Compare avec la semaine précédente pour isoler les changements"},
            {"step": 4, "name": "Notion Radar Briefing", "type": "Publish", "icon": "📊", "desc": "Publie un rapport synthétique avec points d'action"}
        ],
        "faq": [
            {"q": "Le scraper est-il bloqué par Cloudflare ?", "a": "Le blueprint intègre un proxy anti-bot tournant et des délais aléatoires pour garantir 99.8% de succès."}
        ],
        "reviews": [
            {"author": "Alexandre M.", "role": "Product Marketing Manager", "rating": 5, "date": "Il y a 3 jours", "comment": "Nous avons repéré l'augmentation de prix de notre concurrent principal 48h avant l'annonce officielle."}
        ],
        "json_snippet": "{\n  \"name\": \"Competitor Intelligence Radar\",\n  \"nodes\": [\n    { \"name\": \"Cron Weekly\", \"type\": \"n8n-nodes-base.cron\" },\n    { \"name\": \"Headless Scrape\", \"type\": \"n8n-nodes-base.httpRequest\" },\n    { \"name\": \"Claude Diff Analyzer\", \"type\": \"n8n-nodes-base.anthropic\" }\n  ]\n}"
    },
    {
        "id": "tpl_cursor_python_agentic_backend",
        "slug": "cursor-rules-python-fastapi-langchain-chromadb",
        "title": "Cursor AI Rules: Python FastAPI, LangChain & ChromaDB",
        "tagline": "Turn Cursor into a Senior AI Backend Engineer: enforce Pydantic V2, clean architecture & async streaming.",
        "ecosystem": "cursor",
        "category": "AI Developer Tools",
        "price_usd": 29,
        "price_cents": 2900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "VectorOps Academy",
            "slug": "vectorops-academy",
            "badge": "AI Systems Engineer",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=VectorOps",
            "bio": "Ingénieurs backend Python spécialisés dans LangChain v0.3+, FastAPI asynchrone et les bases vectorielles ChromaDB.",
            "website": "https://vectorops.example.com",
            "github": "vectorops",
            "linkedin": "https://linkedin.com/company/vectorops"
        },
        "nodes_count": 5,
        "estimated_hours_saved": 30,
        "monthly_savings_estimate": "Eliminates hallucinated LangChain legacy methods",
        "required_services": ["Cursor IDE", "Python 3.11+", "FastAPI", "LangChain v0.3+"],
        "highlights": [
            "Bans deprecated LangChain v0.1 methods (forces LCEL runnable protocol)",
            "Enforces strict Pydantic v2 schemas and async route handlers",
            "Standardizes vector search retrieval and metadata filtering",
            "Zero memory leaks in Server-Sent Events (SSE) streaming"
        ],
        "sales_count": 138,
        "rating": 5.0,
        "reviews_count": 31,
        "is_featured": False,
        "pipeline_steps": [
            {"step": 1, "name": ".cursorrules Python Core", "type": "IDE Guard", "icon": "🐍", "desc": "Intercepte la génération de code Python dans Cursor"},
            {"step": 2, "name": "LCEL Architecture Enforcer", "type": "AI Guard", "icon": "🔗", "desc": "Exige la syntaxe moderne LangChain Expression Language"},
            {"step": 3, "name": "Async FastAPI Validator", "type": "Performance", "icon": "⚡", "desc": "Garantit des handlers 100% asynchrones sans blocage GIL"},
            {"step": 4, "name": "SSE Streaming Guard", "type": "Streaming", "icon": "🌊", "desc": "Sécurise le flux de tokens en direct vers le frontend"}
        ],
        "faq": [
            {"q": "Ce pack gère-t-il les dernières versions de LangChain ?", "a": "Oui, il est calibré pour LangChain v0.3+ et LangGraph, en bannissant les anciennes fonctions obsolètes."}
        ],
        "reviews": [
            {"author": "Benoit S.", "role": "Lead AI Engineer", "rating": 5, "date": "Il y a 1 semaine", "comment": "Indispensable si vous codez avec Cursor sur des agents Python. Fini les hallucinations de méthodes qui n'existent plus."}
        ],
        "json_snippet": "{\n  \"rules\": [\n    \"Always use LangChain v0.3+ LCEL syntax with pipe operators (|).\",\n    \"Use Pydantic v2 BaseModels with ConfigDict.\",\n    \"Enforce async def on all FastAPI endpoints with type annotations.\"\n  ]\n}"
    },
    {
        "id": "tpl_make_churn_prediction_winback",
        "slug": "make-ai-churn-prediction-retention-winback",
        "title": "Make.com AI In-App Telemetry Churn Predictor & Rescue",
        "tagline": "Detects slipping product usage early and triggers personalized CEO check-in emails before cancellation.",
        "ecosystem": "make",
        "category": "Customer Support",
        "price_usd": 49,
        "price_cents": 4900,
        "platform_fee_percent": 20,
        "creator": {
            "name": "RetentionLab",
            "slug": "retentionlab",
            "badge": "Product-Led Growth Specialist",
            "avatar": "https://api.dicebear.com/7.x/identicon/svg?seed=RetentionLab",
            "bio": "Experts en Product-Led Growth et détection prédictive de désengagement client via télémétrie in-app.",
            "website": "https://retentionlab.example.com",
            "github": "retentionlab",
            "linkedin": "https://linkedin.com/company/retentionlab"
        },
        "nodes_count": 18,
        "estimated_hours_saved": 22,
        "monthly_savings_estimate": "Saves 3 to 7 high-ticket SaaS accounts per month",
        "required_services": ["PostHog / Mixpanel", "Make.com", "OpenAI / Claude", "Gmail / Outlook"],
        "highlights": [
            "Calculates 14-day login & core action dropoff automatically",
            "Crafts ultra-personalized, non-salesy emails from the CEO inbox",
            "Offers customized onboarding call links before churn occurs",
            "Syncs retention health score to CRM for Account Executives"
        ],
        "sales_count": 58,
        "rating": 4.91,
        "reviews_count": 12,
        "is_featured": False,
        "pipeline_steps": [
            {"step": 1, "name": "PostHog Usage Drop Trigger", "type": "Trigger", "icon": "📉", "desc": "Détecte une baisse de 40% d'activité sur 14 jours"},
            {"step": 2, "name": "Feature Adoption Diagnosis", "type": "Analytics", "icon": "📊", "desc": "Analyse les fonctionnalités bloquantes ou inutilisées"},
            {"step": 3, "name": "Personalized CEO Outreach", "type": "AI Prompt", "icon": "✍️", "desc": "Rédige un email bienveillant et axé sur la valeur"},
            {"step": 4, "name": "Customer Success Task Sync", "type": "Task", "icon": "🛎️", "desc": "Crée une alerte prioritaire pour le Customer Success Manager"}
        ],
        "faq": [
            {"q": "Fonctionne-t-il avec Mixpanel ou Segment ?", "a": "Oui, n'importe quel webhook d'analytics produit peut être raccordé en 2 minutes."}
        ],
        "reviews": [
            {"author": "Émilie G.", "role": "Head of Customer Success", "rating": 5, "date": "Il y a 4 jours", "comment": "Nos clients apprécient énormément la démarche préventive. Le taux de réponse dépasse 40%."}
        ],
        "json_snippet": "{\n  \"name\": \"AI Churn Predictor & Retention Winback\",\n  \"blueprint\": {\n    \"flow\": [\n      { \"id\": 1, \"module\": \"analytics:WatchDropoff\" },\n      { \"id\": 2, \"module\": \"openai:DraftPersonalEmail\" },\n      { \"id\": 3, \"module\": \"gmail:SendDirectMail\" }\n    ]\n  }\n}"
    }
]

def main():
    target_paths = [
        ROOT / "data" / "templates_catalog.json",
        ROOT / "site" / "src" / "data" / "templates_catalog.json",
        ROOT / "site" / "public" / "data" / "templates_catalog.json"
    ]

    for path in target_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(TEMPLATES, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] Catalog successfully synced to {path} ({len(TEMPLATES)} blueprints)")

if __name__ == "__main__":
    main()
