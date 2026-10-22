# ⚡ SaaS Radar - Système Média & Affiliation B2B 100% Autonome

Bienvenue dans le moteur **SaaS Radar**, un système conçu pour générer des revenus récurrents d'affiliation SaaS B2B (objectif : **2 000 $/mois**) avec **0 $ de capital initial**, propulsé par des agents d'intelligence artificielle et déployé sur une pile 100 % gratuite.

---

## 🏗️ Architecture du Système Multi-Agents

Ce projet est découpé en deux couches indépendantes :

### 1. Le Cerveau Multi-Agents (`/agents`)
* **Agent 1 : Market Radar (`agents/radar_agent.py`)** : Identifie les logiciels SaaS B2B en pleine croissance avec forte intention d'achat (pricing, avis, comparatifs) et commissions récurrentes élevées.
* **Agent 2 : Senior Technical Analyst (`agents/analyst_agent.py`)** : Utilise l'API Google Gemini (`gemini-3.8-flash`) avec schéma Pydantic strict pour produire des évaluations logicielles approfondies, impartiales, avec tarification précise, vrais pour/contre et FAQ compatibles Google Rich Snippets.
* **Agent 3 : Content Publisher (`agents/publisher_agent.py`)** : Transforme les données en fichiers Markdown/MDX avec frontmatter Zod, et met à jour l'index de recherche instantané (`site/src/data/tools-index.json`).
* **L'Orchestrateur (`agents/orchestrator.py`)** : Pilote l'ensemble de la chaîne en ligne de commande ou via cron automatisé.

### 2. Le Média Web Ultra-Performant (`/site`)
* **Framework** : [Astro 5](https://astro.build) (Score Lighthouse 100/100, 0kb de JavaScript client inutile, SEO maximal).
* **Design** : Tailwind CSS, thème sombre moderne, badges de conversion et cartes de comparaison.
* **SEO Google** : Balisage de données structurées **Schema.org JSON-LD** (`SoftwareApplication`, `Review`, `FAQPage`) pour apparaître dans les encarts spéciaux de Google.
* **Lien Cloaking & Tracking** : Route `/go/[tool]` qui masque les liens d'affiliation avec redirection propre (`rel="sponsored nofollow"`).

### 3. L'Automatisation 100% Autonome (`.github/workflows/auto_publish.yml`)
* Un **GitHub Action gratuit** s'exécute chaque jour à 05:00 UTC.
* Il lance les agents, découvre de nouveaux logiciels, rédige les fiches, commit sur Git et déclenche le redéploiement automatique sur Vercel. **Aucune intervention humaine requise.**

---

## 💰 La Stratégie pour Atteindre 2 000 $/mois avec 0 $

1. **Inscris-toi gratuitement aux réseaux d'affiliation SaaS** :
   * [PartnerStack](https://partnerstack.com)
   * [Rewardful](https://rewardful.com)
   * [Impact.com](https://impact.com)
   * Programmes directs (ex: *Make Affiliate Program*, *HubSpot Partners*, *ElevenLabs Affiliate*).
2. **Ajoute tes liens d'affiliation** dans `agents/config.py` dans le dictionnaire `AFFILIATE_MAP`.
3. **Le calcul des 2 000 $/mois** :
   * Une commission SaaS récurrente moyenne = 30 $/mois par utilisateur actif.
   * **65 utilisateurs abonnés** à travers tes centaines de fiches indexées sur Google = **1 950 $/mois à 2 000 $/mois passifs**.

---

## 🚀 Guide de Démarrage Rapide

### 1. Activer l'Agent avec ta clé Gemini (Gratuite)
1. Récupère ta clé API gratuite sur [Google AI Studio](https://aistudio.google.com).
2. Copie `.env.example` en `.env` et renseigne ta clé :
   ```bash
   cp .env.example .env
   ```

### 2. Générer des Fiches Produits
* **Pour ajouter un outil spécifique** :
  ```bash
  python agents/orchestrator.py --tool "Make" --category "AI Automation"
  ```
* **Pour laisser le radar découvrir automatiquement 3 logiciels tendance** :
  ```bash
  python agents/orchestrator.py --discover 3
  ```

### 3. Lancer le Site en Local
```bash
cd site
npm install
npm run dev
```
Rends-toi sur `http://localhost:4321` pour admirer ton portail !

---

## ☁️ Déploiement Gratuit sur Vercel ($0)

1. Crée un compte gratuit sur [GitHub](https://github.com) et pousse ce dossier :
   ```bash
   git init
   git add .
   git commit -m "Initial commit of SaaS Radar"
   git remote add origin https://github.com/TON-PSEUDO/saas-radar.git
   git push -u origin main
   ```
2. Va sur [Vercel](https://vercel.com) (gratuit) et clique sur **"Add New Project"**.
3. Importe ton dépôt GitHub, sélectionne le dossier racine `site`, et clique sur **Deploy**.
4. Dans les paramètres de ton dépôt GitHub (**Settings > Secrets and variables > Actions**), ajoute ton secret :
   * `GEMINI_API_KEY`: Ta clé Google AI Studio.
5. C'est terminé ! Ton robot autonome tourne chaque matin en toute autonomie.
