# 🧬 Guide d'Exploitation : Helia-AutoEvolution

## 1. Principes Fondamentaux & Sécurité

`Helia-AutoEvolution` fonctionne sur un pipeline d'amélioration continue strictement contrôlé et fondé sur des preuves auditables :

$$\text{Observer} \longrightarrow \text{Diagnostiquer} \longrightarrow \text{Proposer} \longrightarrow \text{Valider} \longrightarrow \text{Déployer} \longrightarrow \text{Mesurer} \longrightarrow \text{Rollback}$$

### Règles impératives de gouvernance
- **Zéro publication autonome non contrôlée** : `Helia-AutoEvolution` ne publie **JAMAIS** seul un article, une fiche, une modification SEO, une newsletter ou un post social.
- **Preuves obligatoires** : Un faible trafic ou un CTR en baisse **ne constitue JAMAIS une preuve suffisante** pour modifier du contenu éditorial ou une note. Une source primaire vérifiée et horodatée est requise.
- **Réversibilité totale (100%)** : Tout déploiement crée un snapshot bit-à-bit dans `reports/snapshots/evo_<id>/` avant toute écriture.
- **Zéro secret / PII** : Tout token, clé d'API ou donnée personnelle est rejeté et masqué avant enregistrement.

---

## 2. Qui Fait la Validation ? (Architecture à Double Verrou)

La validation est assurée par un tandem rigoureux :

### Verrou 1 : Collège d'Agents Spécialisés (Validation Technique & Factuelle)
Selon la cible de la proposition, les agents concernés doivent émettre un vote `APPROVED` :
- **`AnalystAgent`** : Prix, scores Sentinel v2.4, comparatifs, sources primaires et formules TCO.
- **`LinkDoctorAgent`** : URLs, intégrité des redirections edge `_redirects` et statut HTTP 200/301.
- **`DesignJuryAgent`** : Hiérarchie visuelle, ergonomie mobile, contraste et accessibilité.
- **`SecurityAgent`** : Détection des secrets, conformité des en-têtes HTTP et frontières privées.
- **`PublisherAgent`** : Validité du build Astro SSG, syntaxe frontmatter YAML, slug canonique et Schema.org.
- **`Helia-CognitiveCore 5.0`** : Non-régression par rapport à la mémoire immunitaire (`immune_memory.json`).

### Verrou 2 : L'Opérateur Humain (Gatekeeper Obligatoire)
- **Pour tout risque Moyen (`medium`) ou Élevé (`high`)** : La proposition reste bloquée en statut `awaiting_review` tant qu'un humain n'a pas explicitement validé via `approve_human()`.

---

## 3. Guide des Commandes d'Exploitation (CLI Python)

Toutes les opérations d'administration peuvent être exécutées depuis un terminal sécurisé :

### A. Consulter les propositions enregistrées
```python
from agents.auto_evolution_agent import HeliaAutoEvolutionAgent

agent = HeliaAutoEvolutionAgent()

# Lister toutes les propositions en attente de revue
pending = agent.list_proposals(status="awaiting_review")
for p in pending:
    print(f"[{p['id']}] {p['target']['type']}:{p['target']['slug']} | Risque: {p['riskLevel']}")
    print(f"  Problème : {p['problem']}")
    print(f"  Preuves   : {p['evidence']}")
```

### B. Examiner une proposition détaillée par son identifiant
```python
prop = agent.get_proposal("evo_20261106_xxxxxx")
print(prop)
```

### C. Approuver une proposition (Validation Humaine)
```python
agent.approve_human(
    proposal_id="evo_20261106_xxxxxx",
    author="DirecteurHeliaTech",
    rationale="Vérifié avec la documentation officielle du partenaire."
)
```

### D. Rejeter une proposition
```python
agent.reject_proposal(
    proposal_id="evo_20261106_xxxxxx",
    author="DirecteurHeliaTech",
    reason="Preuve insuffisante : donnée non sourcée par un benchmark primaire."
)
```

### E. Déployer une proposition approuvée
```python
# Crée automatiquement le snapshot dans reports/snapshots/ et exécute les pré-contrôles
agent.deploy_proposal(
    proposal_id="evo_20261106_xxxxxx",
    deployer="DirecteurHeliaTech"
)
```

### F. Déclencher un Rollback Immédiat (Restauration Snapshot)
En cas de régression ou d'anomalie constatée :
```python
agent.rollback_proposal(
    proposal_id="evo_20261106_xxxxxx",
    reason="Régression observée dans le rendu mobile.",
    author="DirecteurHeliaTech"
)
```
Le fichier cible est **instantanément restauré bit-à-bit** dans son état exact d'avant déploiement.

---

## 4. Consultation via le Cockpit Sentinel

Rendez-vous dans la console d'administration :
- URL : `https://heliatech.online/sentinel/admin` (ou `/sentinel/suivicontrol`)
- Onglet : **🧬 Auto-Évolution & Génétique**
- Vous y trouverez :
  - Le compteur des propositions par statut (`awaiting_review`, `approved`, `deployed`, `rolled_back`).
  - Le nombre de propositions bloquées faute de preuve (`blocked_insufficient_evidence`).
  - La liste des dernières propositions avec leurs preuves, le statut de validation des agents et les boutons d'action d'approbation et de rollback.
