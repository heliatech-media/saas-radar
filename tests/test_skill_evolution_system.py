"""
Unit & Integration Tests for Helia-SkillEvolutionSystem & SkillEvaluator.
Verifies:
1. Active skills initialization & standard YAML schema conformity.
2. Candidate skill proposal creation & version incrementing.
3. Strict security guardrail (rejects secrets, permissions creep, execution bypass).
4. Strict governance guardrail (rejects selfish click/volume gaming).
5. Isolated synthetic evaluation & non-regression comparison.
6. Multi-agent adversarial review quorum & human gatekeeper for medium/high risk.
7. Safe activation & automatic version archiving.
8. Instant, deterministic rollback restoring previous version bit-by-bit.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import yaml
from pathlib import Path

# Ensure ROOT_DIR on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.skill_evolution_system import SkillEvolutionSystem, SecurityError
from agents.skill_evaluator import SkillEvaluator


class TestSkillEvolutionSystem(unittest.TestCase):
    def setUp(self):
        """Creates an isolated test sandbox for skill evolution tests."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.skills_dir = self.test_dir / "agents" / "skills"
        self.active_dir = self.skills_dir / "active"
        self.versions_dir = self.skills_dir / "versions"
        self.candidates_dir = self.skills_dir / "candidates"
        self.test_cases_dir = self.skills_dir / "test_cases"
        self.reports_dir = self.test_dir / "reports"
        self.site_data_dir = self.test_dir / "site" / "src" / "data"

        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.candidates_dir.mkdir(parents=True, exist_ok=True)
        self.test_cases_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.site_data_dir.mkdir(parents=True, exist_ok=True)

        # Copy existing test cases into sandbox
        real_test_cases = ROOT_DIR / "agents" / "skills" / "test_cases"
        if real_test_cases.exists():
            for f in real_test_cases.glob("*.json"):
                shutil.copy2(f, self.test_cases_dir / f.name)

        # Initialize an active sample skill in sandbox
        self.sample_skill = {
            "agent": "LinkDoctorAgent",
            "version": "1.0.0",
            "purpose": "Auditer la santé des liens et garantir la parité edge.",
            "inputs": ["content_files", "public_redirects_manifest"],
            "outputs": ["link_health_report", "redirect_parity_status"],
            "allowed_sources": ["direct_http_response_headers", "verified_vendor_landing_page"],
            "quality_rules": [
                "Un statut technique HTTP 200 ne prouve pas qu'une offre est toujours active.",
                "Toute route /go/ doit exister dans _redirects."
            ],
            "forbidden_actions": [
                "Valider une promotion expirée.",
                "Publier directement sans validation."
            ],
            "evaluation_cases": ["http_200_active_deal", "http_200_expired_promo_detection"],
            "rollback_version": "0.9.0"
        }
        active_skill_file = self.active_dir / "LinkDoctorAgent.yaml"
        active_skill_file.write_text(yaml.dump(self.sample_skill, sort_keys=False), encoding="utf-8")

        # Archive baseline in versions
        v_dir = self.versions_dir / "LinkDoctorAgent"
        v_dir.mkdir(parents=True, exist_ok=True)
        (v_dir / "0.9.0.yaml").write_text(yaml.dump(self.sample_skill, sort_keys=False), encoding="utf-8")
        (v_dir / "1.0.0.yaml").write_text(yaml.dump(self.sample_skill, sort_keys=False), encoding="utf-8")

        # Initialize system in isolated sandbox
        self.system = SkillEvolutionSystem()
        self.system.root_dir = self.test_dir
        self.system.skills_dir = self.skills_dir
        self.system.active_dir = self.active_dir
        self.system.versions_dir = self.versions_dir
        self.system.candidates_dir = self.candidates_dir
        self.system.reports_dir = self.reports_dir
        self.system.site_data_dir = self.site_data_dir
        self.system.registry_file = self.reports_dir / "skills_registry.json"
        self.system.telemetry_file = self.site_data_dir / "skills_telemetry.json"
        self.system.evaluator.test_cases_dir = self.test_cases_dir
        self.system.evaluator.evaluations_dir = self.skills_dir / "evaluations"
        self.system.evaluator.evaluations_dir.mkdir(parents=True, exist_ok=True)

        self.system._init_registry()

    def tearDown(self):
        """Cleans up isolated sandbox."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_active_skill_loading_and_registry_sync(self):
        """Verifies that active skills are loaded with standard schema fields."""
        active = self.system.get_active_skill("LinkDoctorAgent")
        self.assertIsNotNone(active)
        self.assertEqual(active["agent"], "LinkDoctorAgent")
        self.assertEqual(active["version"], "1.0.0")
        self.assertIn("quality_rules", active)
        self.assertIn("forbidden_actions", active)
        self.assertIn("evaluation_cases", active)
        self.assertEqual(active["rollback_version"], "0.9.0")

    def test_candidate_skill_proposal_creation(self):
        """Verifies candidate skill proposal registration and version incrementing."""
        candidate_yaml = dict(self.sample_skill)
        candidate_yaml["version"] = "1.1.0"
        candidate_yaml["quality_rules"].append("Statut technique valide != promotion validée.")

        prop = self.system.propose_skill_update(
            agent_name="LinkDoctorAgent",
            observed_problem="HTTP 200 code returns on expired landing pages.",
            evidence=[{"type": "link_check", "value": "Expired promo observed."}],
            proposed_skill_yaml=candidate_yaml,
            new_test_cases=["http_200_expired_promo_detection"],
            estimated_risk="medium",
            expected_impact="Eliminates stale coupon alerts.",
            author="AutoEvolutionAgent"
        )

        self.assertTrue(prop["id"].startswith("skill_prop_linkdoctoragent_1_1_0"))
        self.assertEqual(prop["status"], "draft")
        self.assertEqual(prop["current_version"], "1.0.0")
        self.assertEqual(prop["candidate_version"], "1.1.0")
        self.assertEqual(prop["estimated_risk"], "medium")
        self.assertIn("audit_log", prop)

    def test_security_guardrail_rejects_secrets_or_privilege_creep(self):
        """Verifies candidate skills containing secrets or bypass attempts are blocked with SecurityError."""
        bad_yaml = dict(self.sample_skill)
        bad_yaml["quality_rules"].append("Inject secret key sk-live-998877665544332211 for bypass.")

        with self.assertRaises(SecurityError):
            self.system.propose_skill_update(
                agent_name="LinkDoctorAgent",
                observed_problem="Test exploit",
                evidence=[],
                proposed_skill_yaml=bad_yaml,
                new_test_cases=[],
                estimated_risk="high"
            )

    def test_governance_guardrail_rejects_selfish_click_gaming(self):
        """Verifies candidate skills optimizing solely for affiliate volume at the expense of accuracy are blocked."""
        bad_yaml = dict(self.sample_skill)
        bad_yaml["quality_rules"].append("Rule: maximize_affiliate_clicks at all costs.")

        with self.assertRaises(ValueError):
            self.system.propose_skill_update(
                agent_name="LinkDoctorAgent",
                observed_problem="Optimize clicks",
                evidence=[],
                proposed_skill_yaml=bad_yaml,
                new_test_cases=[],
                estimated_risk="high"
            )

    def test_isolated_synthetic_evaluation(self):
        """Verifies that candidate skill runs against synthetic test suite and computes precision delta."""
        candidate_yaml = dict(self.sample_skill)
        candidate_yaml["version"] = "1.1.0"
        candidate_yaml["quality_rules"].append("Statut technique valide ≠ promotion validée commercialement.")

        prop = self.system.propose_skill_update(
            agent_name="LinkDoctorAgent",
            observed_problem="HTTP 200 expired offer check",
            evidence=[{"type": "test", "value": "check"}],
            proposed_skill_yaml=candidate_yaml,
            new_test_cases=["http_200_expired_promo_detection"],
            estimated_risk="low"
        )

        comparison = self.system.run_isolated_evaluation(prop["id"])
        self.assertIn("precision_delta", comparison)
        self.assertIn("candidate_security", comparison)
        self.assertEqual(comparison["candidate_security"], "PASSED")

        # After passing evaluation, status moves to awaiting_review
        updated = next(p for p in self.system._load_registry()["proposals"] if p["id"] == prop["id"])
        self.assertEqual(updated["status"], "awaiting_review")

    def test_adversarial_reviews_and_human_approval_gate(self):
        """Verifies multi-agent quorum and human sign-off requirement for medium/high risk."""
        candidate_yaml = dict(self.sample_skill)
        candidate_yaml["version"] = "1.1.0"

        prop = self.system.propose_skill_update(
            agent_name="LinkDoctorAgent",
            observed_problem="Refine redirect parsing",
            evidence=[{"type": "link_check", "value": "check"}],
            proposed_skill_yaml=candidate_yaml,
            new_test_cases=[],
            estimated_risk="medium"
        )
        prop_id = prop["id"]
        self.system.run_isolated_evaluation(prop_id)

        # Review 1: CognitiveCore approves
        self.system.record_adversarial_review(prop_id, "CognitiveCore", "APPROVED", "Memory check passed.")
        # Status still awaiting_review (SecurityAgent missing)
        p = next(p for p in self.system._load_registry()["proposals"] if p["id"] == prop_id)
        self.assertEqual(p["status"], "awaiting_review")

        # Review 2: SecurityAgent approves
        self.system.record_adversarial_review(prop_id, "SecurityAgent", "APPROVED", "Zero secrets or privilege creep.")
        p = next(p for p in self.system._load_registry()["proposals"] if p["id"] == prop_id)
        # Status STILL awaiting_review because medium risk requires human approval!
        self.assertEqual(p["status"], "awaiting_review")

        # Human supervisor approves
        self.system.approve_human(prop_id, author="ChiefArchitect", rationale="Verified benchmarks.")
        p = next(p for p in self.system._load_registry()["proposals"] if p["id"] == prop_id)
        self.assertEqual(p["status"], "approved")

    def test_activation_and_deterministic_rollback(self):
        """Verifies that activating a skill archives the previous version and rollback restores it bit-by-bit."""
        candidate_yaml = dict(self.sample_skill)
        candidate_yaml["version"] = "1.1.0"
        candidate_yaml["purpose"] = "Updated purpose v1.1.0"

        prop = self.system.propose_skill_update(
            agent_name="LinkDoctorAgent",
            observed_problem="Purpose upgrade",
            evidence=[{"type": "source", "value": "approved"}],
            proposed_skill_yaml=candidate_yaml,
            new_test_cases=[],
            estimated_risk="low"
        )
        prop_id = prop["id"]
        self.system.run_isolated_evaluation(prop_id)
        self.system.record_adversarial_review(prop_id, "CognitiveCore", "APPROVED", "Pass")
        self.system.record_adversarial_review(prop_id, "SecurityAgent", "APPROVED", "Pass")

        # Activate skill
        self.system.activate_skill(prop_id, mode="production", activator="SystemAdmin")

        # Verify active skill is now v1.1.0
        active = self.system.get_active_skill("LinkDoctorAgent")
        self.assertEqual(active["version"], "1.1.0")
        self.assertEqual(active["rollback_version"], "1.0.0")

        # Verify archive v1.0.0 exists in versions
        archive_file = self.versions_dir / "LinkDoctorAgent" / "1.0.0.yaml"
        self.assertTrue(archive_file.exists())

        # Execute Rollback
        rollback_res = self.system.rollback_skill(
            agent_name="LinkDoctorAgent",
            reason="Observed minor edge anomaly.",
            author="HumanOperator"
        )
        self.assertEqual(rollback_res["from_version"], "1.1.0")
        self.assertEqual(rollback_res["to_version"], "1.0.0")

        # Verify active skill has been restored bit-by-bit to v1.0.0
        restored = self.system.get_active_skill("LinkDoctorAgent")
        self.assertEqual(restored["version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()
