import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_PUBLIC = ROOT_DIR / "site" / "public"
DOWNLOADS_DIR = SITE_PUBLIC / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

pdf_output_path = DOWNLOADS_DIR / "HeliaTech_Guide_Complet_Architecture_et_Business.pdf"

html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>HeliaTech Media — Dossier Stratégique & Guide Opérationnel Complet</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

  @page {
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: counter(page) " / " counter(pages);
      font-family: 'JetBrains Mono', monospace;
      font-size: 8pt;
      color: #64748b;
    }
  }

  body {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #ffffff;
    color: #0f172a;
    line-height: 1.55;
    font-size: 9.5pt;
    margin: 0;
    padding: 0;
  }

  .font-mono {
    font-family: 'JetBrains Mono', monospace;
  }

  /* Cover Header */
  .header-capsule {
    display: inline-block;
    padding: 4px 12px;
    background: #0f172a;
    color: #38bdf8;
    border-radius: 999px;
    font-size: 7.5pt;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 12px;
  }

  h1 {
    font-size: 24pt;
    font-weight: 900;
    color: #020617;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
    line-height: 1.15;
  }

  .subtitle {
    font-size: 11pt;
    color: #475569;
    margin-bottom: 20px;
    font-weight: 400;
  }

  .meta-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1.5px solid #e2e8f0;
    border-bottom: 1.5px solid #e2e8f0;
    padding: 8px 0;
    margin-bottom: 24px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 7.5pt;
    color: #64748b;
  }

  h2 {
    font-size: 13pt;
    font-weight: 800;
    color: #0f172a;
    border-left: 4px solid #0284c7;
    padding-left: 10px;
    margin: 22px 0 10px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  h3 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #1e293b;
    margin: 14px 0 6px 0;
  }

  p {
    margin: 0 0 10px 0;
    color: #334155;
  }

  /* Highlight Callout Box */
  .callout {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #06b6d4;
    border-radius: 8px;
    padding: 12px 14px;
    margin: 14px 0;
  }

  .callout-title {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 8.5pt;
    color: #0891b2;
    margin-bottom: 4px;
    text-transform: uppercase;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0 16px 0;
    font-size: 8.5pt;
  }

  th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 7px 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 7.5pt;
    letter-spacing: 0.5px;
  }

  td {
    padding: 7px 10px;
    border-bottom: 1px solid #e2e8f0;
    color: #334155;
  }

  tr:nth-child(even) td {
    background-color: #f8fafc;
  }

  .badge {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 7pt;
    font-weight: 700;
  }

  .badge-blue { background: #e0f2fe; color: #0369a1; }
  .badge-green { background: #dcfce7; color: #15803d; }
  .badge-purple { background: #f3e8ff; color: #7e22ce; }
  .badge-amber { background: #fef3c7; color: #b45309; }

  .page-break {
    page-break-before: always;
  }

  /* Diagram Flow */
  .diagram-flow {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    margin: 14px 0;
  }

  .flow-step {
    flex: 1;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
  }

  .flow-num {
    display: inline-block;
    width: 20px;
    height: 20px;
    background: #0f172a;
    color: #fff;
    border-radius: 50%;
    font-size: 8pt;
    line-height: 20px;
    font-weight: 700;
    margin-bottom: 4px;
  }

  .flow-title {
    font-weight: 700;
    font-size: 8pt;
    color: #0f172a;
    margin-bottom: 2px;
  }

  .flow-desc {
    font-size: 7pt;
    color: #64748b;
  }

  ul {
    margin: 4px 0 10px 18px;
    padding: 0;
  }

  li {
    margin-bottom: 4px;
  }
</style>
</head>
<body>

  <!-- PAGE 1: VISION GLOBALE & ARCHITECTURE -->
  <div>
    <div class="header-capsule">DOSSIER STRATÉGIQUE CONFIDENTIEL • HELIATECH MEDIA</div>
    <h1>HeliaTech Media — Guide Opérationnel & Architecture</h1>
    <div class="subtitle">Comprendre l'infrastructure autonome, le modèle d'affaires, les outils partenaires et la génération de revenus récurrents (MRR).</div>

    <div class="meta-bar">
      <span>ENTITÉ : HELIATECH MEDIA (heliatech.online)</span>
      <span>VERSION : 5.0 (AUTONOME)</span>
      <span>DATE : OCTOBRE 2026</span>
    </div>

    <div class="callout">
      <div class="callout-title">💡 La Définition du Projet en 1 Phrase</div>
      <p style="margin: 0; font-weight: 500; font-size: 9.5pt;">
        <strong>HeliaTech</strong> est un média d'ingénierie et un comparateur indépendant de logiciels B2B & IA, <strong>100% piloté et alimenté par 23 agents d'intelligence artificielle</strong>. Son objectif : attirer les décideurs tech prêts à acheter un logiciel et encaisser des <strong>commissions mensuelles récurrentes (20% à 40%)</strong> à chaque abonnement généré.
      </p>
    </div>

    <h2>1. Les 3 Grands Groupes d'Outils du Projet</h2>
    <p>Pour dissiper toute confusion, le projet s'articule autour de trois catégories bien distinctes :</p>

    <table>
      <thead>
        <tr>
          <th>Catégorie</th>
          <th>De quoi s'agit-il ?</th>
          <th>Exemples d'outils</th>
          <th>Rôle exact pour nous</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Groupe 1 : Notre Usine</strong></td>
          <td>Les technologies qui créent, hébergent et protègent notre site.</td>
          <td><span class="badge badge-blue">Astro</span> <span class="badge badge-blue">Cloudflare</span> <span class="badge badge-blue">Flotte 23 Agents</span></td>
          <td>Produire du contenu, maintenir le site en ligne et router les liens sans coût salarial.</td>
        </tr>
        <tr>
          <td><strong>Groupe 2 : Les Partenaires</strong></td>
          <td>Les logiciels B2B dont nous faisons l'évaluation sur le blog.</td>
          <td><span class="badge badge-green">Make</span> <span class="badge badge-green">Supabase</span> <span class="badge badge-green">ElevenLabs</span> <span class="badge badge-green">HeyGen</span></td>
          <td>Ce sont nos <strong>sources de revenus</strong> : ils nous versent des commissions d'affiliation.</td>
        </tr>
        <tr>
          <td><strong>Groupe 3 : L'Encaissement</strong></td>
          <td>Les réseaux de paiement d'affiliation et passerelles bancaires.</td>
          <td><span class="badge badge-purple">Rewardful</span> <span class="badge badge-purple">PartnerStack</span> <span class="badge badge-purple">Stripe</span></td>
          <td>Comptabiliser nos ventes et virer l'argent chaque mois sur notre compte.</td>
        </tr>
      </tbody>
    </table>

    <h2>2. L'Infrastructure Interne (Notre Usine Numérique)</h2>

    <h3>A. La Flotte des 23 Agents Python (Helia)</h3>
    <p>Une agence de presse tech classique emploie 15 personnes (rédacteurs, designers, experts SEO, administrateurs système). Helia remplace cette équipe par 23 sous-agents autonomes :</p>
    <ul>
      <li><strong>Helia-TrendScout & Radar :</strong> Détectent les logiciels émergents sur GitHub, X et Google avant les concurrents.</li>
      <li><strong>Helia-Analyst & ContentFactory :</strong> Rédigent des masterclasses de 2 000+ mots en anglais avec benchmarks réels.</li>
      <li><strong>Helia-VisualArtist :</strong> Génère les visuels 1200x630 vectoriels SVG et les cartes de partage social PNG.</li>
      <li><strong>Helia-AutoEvolution (Agent #23) :</strong> Analyse le trafic réel, améliore les pages existantes et immunise le code contre toute erreur.</li>
      <li><strong>Helia-EdgePublisher :</strong> Compile les 140 pages et les déploie instantanément sur Cloudflare Edge.</li>
    </ul>

    <h3>B. Astro 5 & Cloudflare Edge</h3>
    <ul>
      <li><strong>Astro :</strong> Moteur de rendu statique ultra-performant. Le site charge en moins de 0.1s (note 100/100 sur Google Lighthouse).</li>
      <li><strong>Cloudflare Pages :</strong> Hébergement gratuit sur plus de 300 datacenters dans le monde. Gère les redirections <code>/go/*</code> pour poser les cookies partenaires instantanément.</li>
    </ul>
  </div>

  <!-- PAGE 2: BUSINESS MODEL, PARTENAIRES & ENCAISSEMENT -->
  <div class="page-break">
    <h2>3. Les Logiciels Partenaires & Le Modèle Financier</h2>
    <p>Voici les logiciels phares analysés sur HeliaTech et le calcul de vos commissions récurrentes :</p>

    <table>
      <thead>
        <tr>
          <th>Logiciel</th>
          <th>Secteur / Utilité</th>
          <th>Abonnement Moyen</th>
          <th>Taux Commission</th>
          <th>Gain Récurrent par Client</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Make</strong></td>
          <td>Automatisation de flux (Alternative Zapier)</td>
          <td>120 $/mois</td>
          <td><span class="badge badge-green">30% récurrent</span></td>
          <td><strong>36 $ / mois</strong></td>
        </tr>
        <tr>
          <td><strong>ElevenLabs</strong></td>
          <td>Génération & Synthèse de voix IA</td>
          <td>99 $/mois</td>
          <td><span class="badge badge-green">22% - 30%</span></td>
          <td><strong>25 $ / mois</strong></td>
        </tr>
        <tr>
          <td><strong>HeyGen</strong></td>
          <td>Avatars vidéo IA & Traduction labiale</td>
          <td>180 $/mois</td>
          <td><span class="badge badge-green">25% récurrent</span></td>
          <td><strong>45 $ / mois</strong></td>
        </tr>
        <tr>
          <td><strong>Beehiiv / Rewardful</strong></td>
          <td>Plateformes Newsletter & Paiements Stripe</td>
          <td>100 $/mois</td>
          <td><span class="badge badge-green">30% récurrent</span></td>
          <td><strong>30 $ / mois</strong></td>
        </tr>
        <tr>
          <td><strong>Apollo.io</strong></td>
          <td>Base de prospection B2B & Leads</td>
          <td>199 $/mois</td>
          <td><span class="badge badge-green">30% récurrent</span></td>
          <td><strong>60 $ / mois</strong></td>
        </tr>
        <tr>
          <td><strong>Papaya Global</strong></td>
          <td>Gestion de paie internationale & EOR</td>
          <td>600 $/mois</td>
          <td><span class="badge badge-green">20% récurrent</span></td>
          <td><strong>120 $ / mois</strong></td>
        </tr>
      </tbody>
    </table>

    <div class="callout">
      <div class="callout-title">📈 Simulation Financière : L'Effet Cumulatif SaaS</div>
      <p style="margin: 0;">
        Si HeliaTech apporte seulement <strong>150 clients actifs répartis sur ces outils</strong>, vos gains récurrents s'élèvent à :<br>
        <strong>~6 500 $ USD / mois</strong> (soit environ <strong>78 000 $ USD par an</strong> de revenus passifs automatisés).<br>
        <em>Tant que le client utilise l'outil pour son entreprise, vous touchez votre commission chaque mois sans travail additionnel.</em>
      </p>
    </div>

    <h2>4. Le Parcours de la Vente (De 0 € à l'Encaissement)</h2>
    <div class="diagram-flow">
      <div class="flow-step">
        <div class="flow-num">1</div>
        <div class="flow-title">Recherche</div>
        <div class="flow-desc">Le client cherche une solution sur Google ou Reddit.</div>
      </div>
      <div class="flow-step">
        <div class="flow-num">2</div>
        <div class="flow-title">HeliaTech</div>
        <div class="flow-desc">Il lit notre comparatif chiffré et indépendant.</div>
      </div>
      <div class="flow-step">
        <div class="flow-num">3</div>
        <div class="flow-title">Clic /go/*</div>
        <div class="flow-desc">Le cookie de tracking est déposé (30-90 jours).</div>
      </div>
      <div class="flow-step">
        <div class="flow-num">4</div>
        <div class="flow-title">Abonnement</div>
        <div class="flow-desc">Le client souscrit à l'outil partenaire.</div>
      </div>
      <div class="flow-step">
        <div class="flow-num">5</div>
        <div class="flow-title">Paiement</div>
        <div class="flow-desc">Virement automatique mensuel sur votre compte.</div>
      </div>
    </div>

    <h2>5. La Stratégie d'Acquisition de Trafic</h2>
    <p>Un site web sans visiteurs ne produit aucun revenu. HeliaTech utilise 3 leviers simultanés :</p>
    <ul>
      <li><strong>Google Organic SEO :</strong> Nos duels 1v1 (<em>Make vs Zapier</em>, <em>ElevenLabs vs HeyGen</em>) ciblent des acheteurs qui ont leur carte de crédit à la main.</li>
      <li><strong>Le Badge Trojan (Cheval de Troie) :</strong> Les entreprises lauréates insèrent nos badges de victoire sur leur site, nous créant des backlinks puissants et un flux continu de visiteurs.</li>
      <li><strong>L'Infiltration Reddit :</strong> Les discussions Reddit dominent les premiers résultats Google. En publiant nos réponses techniques rédigées par l'agent, nous captons immédiatement des centaines de prospects qualifiés.</li>
    </ul>

    <h2>6. Synthèse : Votre Rôle en Tant que Fondateur</h2>
    <p>Vous n'avez pas besoin de coder, d'écrire des articles de 2 000 mots ou de concevoir des images. Vos agents s'en chargent 24h/24.</p>
    <p><strong>Vos seules actions à forte valeur ajoutée :</strong></p>
    <ol style="margin-left: 20px; padding: 0; color: #334155; font-size: 9pt;">
      <li>Surveiller le cockpit privé sur <code>https://heliatech.online/sentinel/suivicontrol</code>.</li>
      <li>Copier-coller de temps en temps une réponse ciblée sur Reddit ou LinkedIn pour injecter du carburant immédiat.</li>
      <li>Vérifier vos soldes sur vos tableaux de bord Rewardful et PartnerStack le 1er de chaque mois.</li>
    </ol>
  </div>

</body>
</html>
"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_content(html_content)
    page.pdf(
        path=str(pdf_output_path),
        format="A4",
        print_background=True,
        margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"}
    )
    browser.close()

print(f"SUCCESS: PDF generated at: {pdf_output_path}")
print(f"File size: {pdf_output_path.stat().st_size} bytes")
