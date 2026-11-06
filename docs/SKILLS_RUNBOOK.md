# 🧬 Guide d'Exploitation : Système d'Auto-Amélioration des Skills HeliaTech

## 1. Principes & Sécurité des Skills

Chaque agent HeliaTech opère selon un **skill déclaratif, versionné et auditable** (`.yaml`) définissant strictement son rôle, ses entrées, ses sorties, ses sources autorisées, ses règles de qualité et ses limites.

$$\text{Observer} \longrightarrow \text{Diagnostiquer} \longrightarrow \text{Proposer } v(N+1) \longrightarrow \text{Évaluer (Sandbox)} \longrightarrow \text{Approuver} \longrightarrow \text{Activer} \longrightarrow \text{Mesurer} \longrightarrow \text{Rollback}$$

### Règles d'or
1. **Zéro auto-modification en production** : Aucun agent ne peut modifier directement son propre skill actif.
2. **Banc d'essai obligatoire** : Tout skill candidat doit passer l'évaluation synthétique isolée (`SkillEvaluator`) sans régression de précision, de rejet ni de sécurité.
3. **Double verrou pour risque moyen/élevé** : Quorum technique d'agents (`CognitiveCore`, `SecurityAgent`, etc.) + validation humaine explicite.
4. **Zéro dérive de privilèges (Anti-Privilege Creep)** : Tout ajout de secrets, contournement de validation ou permission d'exécution arbitraire est immédiatement bloqué avec `SecurityError`.
5. **Zéro optimisation purement mercantile** : Interdiction formelle d'optimiser un skill uniquement pour le volume de publication ou les clics d'affiliation.

---

## 2. Format Standard d'un Skill (`agents/skills/active/<AgentName>.yaml`)

```yaml
agent: LinkDoctorAgent
version: 1.0.0
purpose: "Auditer la santé des liens internes/externes et garantir la validité commerciale."
inputs:
  - content_files
  - public_redirects_manifest
outputs:
  - link_health_report
  - commercial_validity_verdict
allowed_sources:
  - direct_http_response_headers
  - verified_vendor_landing_page
quality_rules:
  - "Un statut technique HTTP 200 ne prouve pas qu'une offre est toujours active (statut technique valide ≠ promotion validée)."
  - "Toute route /go/ doit exister dans site/public/_redirects."
forbidden_actions:
  - "Valider une promotion expirée sur la seule base d'un code HTTP 200."
  - "Publier directement sans validation."
evaluation_cases:
  - http_200_active_deal
  - http_200_expired_promo_detection
rollback_version: 0.9.0
```

---

## 3. Comment Ajouter un Cas de Test d'Évaluation Synthétique

Les cas de test sont stockés dans `agents/skills/test_cases/<agent>_test_cases.json`.

Pour ajouter un nouveau test :
1. Ouvrez ou créez le fichier JSON correspondant dans `agents/skills/test_cases/`.
2. Ajoutez un cas de test respectant la structure synthétique (zéro donnée personnelle) :

```json
{
  "id": "http_200_expired_promo_detection",
  "type": "contradictory",
  "payload": {
    "url": "https://partner.example.com/promo",
    "http_status": 200,
    "page_content": "This promotional discount expired on October 31, 2024.",
    "redirect_target": "https://partner.example.com"
  },
  "expected_decision": "REJECT",
  "rule_tested": "Statut technique valide (HTTP 200) != promotion validée commercialement."
}
```

3. Exécutez le banc d'essai pour valider la prise en compte :
```bash
python -c "from agents.skill_evaluator import SkillEvaluator; ev = SkillEvaluator(); print(ev.load_test_cases('LinkDoctorAgent'))"
```

---

## 4. Comment Proposer, Évaluer et Approuver une Nouvelle Version

Toutes les étapes du cycle de vie peuvent être orchestrées via le script Python `agents/skill_evolution_system.py` :

### A. Proposer une version candidate v(N+1)
```python
from agents.skill_evolution_system import SkillEvolutionSystem

system = SkillEvolutionSystem()
active = system.get_active_skill("LinkDoctorAgent")

candidate_yaml = dict(active)
candidate_yaml["version"] = "1.1.0"
candidate_yaml["quality_rules"].append("Statut technique valide ≠ promotion validée commercialement.")

prop = system.propose_skill_update(
    agent_name="LinkDoctorAgent",
    observed_problem="Des codes HTTP 200 sont retournés sur des pages dont la promotion est expirée.",
    evidence=[{"type": "link_check", "value": "Offres expirées avec code 200"}],
    proposed_skill_yaml=candidate_yaml,
    new_test_cases=["http_200_expired_promo_detection"],
    estimated_risk="medium",
    expected_impact="Élimine les faux positifs de bons plans.",
    author="DirecteurTechnique"
)
print("Proposition créée :", prop["id"])
```

### B. Lancer l'évaluation synthétique isolée
```python
comparison = system.run_isolated_evaluation(prop["id"])
print(f"Δ Précision: {comparison['precision_delta']}% | Sécurité: {comparison['candidate_security']}")
```

### C. Consigner les revues contradictoires d'agents
```python
system.record_adversarial_review(prop["id"], "CognitiveCore", "APPROVED", "Conforme à la mémoire des incidents passés.")
system.record_adversarial_review(prop["id"], "SecurityAgent", "APPROVED", "Aucun secret ni élévation de privilèges.")
```

### D. Approuver la version (Validation Humaine)
```python
system.approve_human(
    proposal_id=prop["id"],
    author="DirecteurHeliaTech",
    rationale="Banc d'essai réussi avec +12% de précision sur la détection des faux deals."
)
```

---

## 5. Comment Activer et Restaurer (Rollback)

### A. Activer le skill approuvé
```python
system.activate_skill(
    proposal_id=prop["id"],
    mode="production",
    activator="DirecteurHeliaTech"
)
```
*Le système archive automatiquement l'ancienne version dans `agents/skills/versions/<AgentName>/1.0.0.yaml` et déploie la nouvelle dans `active/`.*

### B. Restaurer immédiatement une version antérieure (Rollback déterministe)
En cas de régression ou sur simple demande :
```python
system.rollback_skill(
    agent_name="LinkDoctorAgent",
    reason="Régression observée dans les redirections edge.",
    author="DirecteurHeliaTech"
)
```
*Le fichier `agents/skills/active/LinkDoctorAgent.yaml` est instantanément restauré bit-à-bit depuis la version d'archive, le registre est mis à jour et la télémétrie Sentinel est actualisée.*

---

## 6. Consultation dans le Cockpit Sentinel

Rendez-vous sur :
- `https://heliatech.online/sentinel/admin` (ou `/sentinel/suivicontrol`)
- Onglet : **🧬 Auto-Évolution & Génétique**
- Section : **Registre des Skills Versionnés & Auto-Amélioration des Agents (24 Agents)**
  - Statut des 6 skills prioritaires (`v1.0.0`).
  - Nombre de règles de qualité et d'actions interdites.
  - Cibles de rollback immédiat (`v0.9.0`).
  - Bouton 1-click pour déclencher un rollback d'urgence.
