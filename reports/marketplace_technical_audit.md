# RAPPORT D'AUDIT TECHNIQUE COMPLET — PHASE 0
## Projet : Transformation de HeliaTech en Marketplace Multi-Vendeurs de Produits Digitaux
**Date :** 5 Novembre 2026  
**Équipe d'ingénierie :** Senior Software Architect, Full-Stack Developer, UI/UX Designer & Security Engineer  
**Statut :** PHASE 0 COMPLETED  

---

### 1. Analyse de l'Architecture & de l'Application Existante

#### 1.1 Stack Frontend & Framework Web
* **Framework :** Astro v5.4.2 avec intégration `@astrojs/tailwind` (Tailwind CSS v3.4.17) et `@tailwindcss/typography`.
* **Mode de rendu :** `output: 'static'` (Static Site Generation — SSG). Le site compile actuellement **342 pages statiques** ultra-rapides (`/reviews/`, `/versus/`, `/blog/`, `/sentinel/`, `/templates/`, etc.) avec `trailingSlash: 'always'`.
* **Design System :** Thème B2B "Dark Glassmorphism" avec palette de couleurs contrastées :
  * Fond sombre : `#030303` et `slate-950/80`
  * Accents visuels : Cyan (`#06b6d4`), Émeraude (`#10b981`), Indigo (`#6366f1`) et Ambre (`#f59e0b`)
  * Typographie : `Space Grotesk`, `Inter` et `JetBrains Mono`
* **Composants transverses :** `Layout.astro`, `SpotlightCommandPalette.astro`, `LeadMagnetDrawer.astro`.

#### 1.2 Stack Backend & Infrastructure Serverless
* **Hébergement & CDN :** Cloudflare Pages avec zone DNS Cloudflare active (`CLOUDFLARE_ZONE_ID`).
* **Fonctions Serverless (Edge Runtime) :** Cloudflare Pages Functions déployées dans `site/functions/api/` et `functions/api/` :
  * `/api/subscribe` : Capture de leads email B2B, distribution d'alertes Telegram instantanées et emails transactionnels via Resend API.
  * `/api/telemetry` : Endpoint d'ingestion de télémétrie respectueux de la vie privée.
* **Flotte d'Agents Autonomes :** Daemon Python 3.14 (`run_helia_daemon.py`) orchestrant des agents d'analyse, d'affiliation et de modération (`agents/`).

#### 1.3 État Actuel des Données et du Stockage
* **Données de contenu actuelles :**
  * Collections Markdown : `site/src/content/reviews` (80+ audits logiciels) et `site/src/content/blog` (40+ guides d'architecture).
  * Fichiers JSON locaux : `site/src/data/templates_catalog.json` (catalogue de 12 templates prototypes), `site/src/data/tools-index.json`.
  * Persistance client sur `/portal/` : Gestion d'état locale via `localStorage` (`_ht_user_session`, `_ht_buyer_purchases`, `_ht_buyer_wishlist`, `_ht_seller_products`, `_ht_seller_inbox`, `_ht_buyer_b2b`, `_ht_seller_profile`).
* **Base de données SQL :**
  * Un schéma initial a été modélisé dans `data/marketplace_schema.sql` (PostgreSQL / Supabase avec tables `creators`, `templates`, `orders` et RLS). **Aucune base SQL n'est encore connectée en temps réel au frontend.**

#### 1.4 Écrans Marketplace Déjà Disponibles en Pré-lancement (Staging Discret)
1. `/templates/` (`site/src/pages/templates/index.astro`) : Grille de catalogue avec filtrage par écosystème (`n8n`, `Make`, `Airtable`, `Cursor`), recherche et catégories.
2. `/templates/[slug]/` (`site/src/pages/templates/[slug].astro`) : Fiche technique produit détaillée avec étapes de pipeline, prérequis, highlights, bio créateur et FAQ.
3. `/creator/[slug]/` (`site/src/pages/creator/[slug].astro`) : Vitrine publique des créateurs avec catalogue de leurs créations.
4. `/sell/` (`site/src/pages/sell/index.astro`) : Page d'atterrissage "Devenir Vendeur" avec simulateur de gains 80%.
5. `/portal/` (`site/src/pages/portal/index.astro`) : Double espace Acheteur / Vendeur avec Auth Gate, gestion de bibliothèque, téléchargement JSON, facturation B2B et scanner Sentinel Anti-Scam.

---

### 2. Ce Qui Manque Pour Une Marketplace Réelle de Production

| Composant | État Actuel (Staging) | Exigence de Production Visée |
| :--- | :--- | :--- |
| **Base de Données** | Fichiers JSON statiques + `localStorage` client | Base relationnelle PostgreSQL (Supabase / Cloudflare D1) avec 29 tables, intégrité référentielle, index composites et transactions ACID. |
| **Authentification** | Session locale `_ht_user_session` dans le navigateur | Authentification serveur centralisée (Supabase Auth / JWT HttpOnly) avec 4 rôles stricts (`USER`, `SELLER`, `ADMIN`, `SUPER_ADMIN`). |
| **Stockage Fichiers** | Fichiers simulés / JSON client | Stockage d'objets privé chiffré (Cloudflare R2 ou Supabase Private Storage) avec URLs pré-signées temporaires (TTL 15 min). |
| **Paiements** | Boutons de commande démo | Prestataire de paiement multi-vendeurs (Stripe Connect / Lemon Squeezy / Paddle) avec calcul de split 80/20, gestion de TVA et webhooks signés idempotents. |
| **Modération & Admin** | Code disséminé dans Sentinel | Dashboard Administrateur dédié (`/admin/marketplace`) avec file de validation des templates, gestion des vendeurs et audit logs. |
| **Protection Fichiers** | Scanner client sommaire | Moteur Sentinel Anti-Scam côté serveur (vérification AST des nœuds n8n/Make, purge de secrets d'API, anti-phishing). |

---

### 3. Changements Nécessaires SANS Casser l'Application Existante

#### 3.1 Règle d'Invariance Absolue
* **Le moteur de publication éditoriale Astro ne sera JAMAIS perturbé :** Les 342 pages statiques existantes (analyses logicielles, duels de SaaS, articles de blog, redirections `/go/`) continuent d'être générées avec une vitesse maximale.
* **Architecture Hybride Découplée :**
  * Les pages publiques marketing et fiches templates (`/templates/`, `/templates/[slug]/`, `/creator/[slug]/`) conservent leur rendu SSG/ISR ultra-rapide pour un référencement Google optimal.
  * Les dashboards (`/dashboard/`, `/seller/`, `/admin/marketplace`) et les API transactionnelles (`/api/marketplace/*`) sont propulsés dynamiquement par les **Cloudflare Pages Functions**.

#### 3.2 Schéma Modulaire de Base de Données (29 Tables)
Le schéma PostgreSQL / Supabase est structuré en domaines fonctionnels indépendants :
1. **Identité & Rôles :** `seller_profiles`, `seller_applications`
2. **Catalogue & Taxonomie :** `marketplace_categories`, `marketplace_products`, `product_media`, `product_files`, `product_versions`, `product_tags`, `product_tag_relations`, `product_licenses`
3. **Engagement & Social :** `product_favorites`, `reviews`, `review_replies`, `product_reports`
4. **Ventes & Transactions :** `orders`, `order_items`, `purchases`, `payments`, `payment_events`, `product_bundles`, `bundle_items`, `seller_promotions`, `promotion_redemptions`
5. **Finances & Versements :** `seller_payouts`
6. **Support & Service Après-Vente :** `support_tickets`, `support_messages`
7. **Système & Audit :** `seller_notifications`, `marketplace_notifications`, `admin_audit_logs`

---

### 4. Plan d'Intégration par Phases (Roadmap Technique)

* [x] **PHASE 0 — Audit & Architecture Globale** : Analyse intégrale, cartographie des flux et définition du plan d'ingénierie.
* [ ] **PHASE 1 — Base de Données & Migrations Modulaires** : Écriture et application du schéma SQL complet des 29 tables avec clés étrangères, index de recherche, types monétaires exacts (entiers en centimes) et Row-Level Security (RLS).
* [ ] **PHASE 2 — Authentification, Sessions & Contrôle des Rôles** : Mise en place du middleware d'autorisation serveur pour les 4 rôles (`USER`, `SELLER`, `ADMIN`, `SUPER_ADMIN`) et flux de candidature vendeur.
* [ ] **PHASE 3 — Marketplace Publique Connectée** : Connexion de `/templates/`, des catégories, des filtres multi-critères et des fiches produits sur la base de données réelle.
* [ ] **PHASE 4 — Dashboard Acheteur (`/dashboard`)** : Bibliothèque personnelle persistante, téléchargements sécurisés, historique de commandes, gestion des favoris et tickets de support.
* [ ] **PHASE 5 — Seller Studio (`/seller`)** : Assistant de publication en 7 étapes, gestion des versions de blueprints avec changelog, analytics financiers et relevés de gains.
* [ ] **PHASE 6 — Dashboard Administrateur (`/admin/marketplace`)** : File de validation et modération des templates, approbation des vendeurs, gestion des commissions et des catégories.
* [ ] **PHASE 7 — Paiements, Webhooks & Livraison Numérique** : Intégration de l'abstraction `PaymentProvider`, validation serveur des commandes, split 80/20 et génération de tokens signés éphémères pour les fichiers.
* [ ] **PHASE 8 — Recette Finale, Sécurité & QA** : Tests de charge, tests d'autorisation, validation antivirus/anti-scam et documentation technique complète.

---

### 5. Identification des Risques Techniques & Stratégie d'Atténuation

1. **Risque de fuite des fichiers payants :**
   * *Atténuation :* Les fichiers `.json`, `.zip` ou `.sql` ne sont **jamais stockés dans le dossier public d'Astro**. Ils sont déposés dans un bucket de stockage privé. L'accès est conditionné à une commande au statut `paid`, avec délivrance d'une URL signée valide 15 minutes seulement.
2. **Risque de présence de secrets ou clés API dans les templates :**
   * *Atténuation :* Analyse automatique de contenu lors du dépôt (détection regex de `sk-`, `sk_live_`, `ghp_`, tokens Bearer, mots de passe de bases de données) avant toute mise en ligne.
3. **Risque d'exécution de code malveillant :**
   * *Atténuation :* Les fichiers sont traités comme des ressources textuelles passives à inspecter par l'acheteur, jamais exécutés sur le serveur de la marketplace.
4. **Risque de double validation ou d'incohérence financière sur les webhooks :**
   * *Atténuation :* Table `payment_events` avec contrainte d'idempotence stricte sur l'ID de transaction externe. Tous les montants financiers sont manipulés en centimes entiers (`INTEGER`), interdisant les approximations de nombres flottants.

---

### PHASE STATUS
* **Phase :** PHASE 0 — AUDIT COMPLET DU PROJET EXISTANT
* **Status :** COMPLETED
* **Fonctionnalités auditées :** 342 pages SSG, Cloudflare Functions API, collections Markdown, schémas DDL, dashboards de staging.
* **Fichiers créés :** `reports/marketplace_technical_audit.md`
* **Fichiers modifiés :** Aucun (audit 100% non-destructif).
* **Risques restants :** Nécessité d'associer une instance PostgreSQL/Supabase active pour accueillir les tables de la Phase 1.
* **Prochaine étape :** Lancement de la **PHASE 1 — ARCHITECTURE ET DATABASE** (Création et déploiement des 29 tables et des migrations SQL).
