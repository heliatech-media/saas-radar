"""
Unit & Integration Tests for Helia-AutoEvolution Controlled Improvement Pipeline.
Verifies:
1. Proposal creation and schema adherence.
2. Evidence sufficiency rules (low traffic alone strictly blocked).
3. Multi-agent review gating & rejection handling.
4. Mandatory human gatekeeper for medium & high risk.
5. Snapshot creation and safe deployment.
6. Pre-deployment cybersecurity secret leak prevention.
7. Deterministic bit-exact rollback restoration.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Ensure ROOT_DIR on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.auto_evolution_agent import HeliaAutoEvolutionAgent, SecurityError


class TestHeliaAutoEvolutionPipeline(unittest.TestCase):
    def setUp(self):
        """Creates an isolated temporary test sandbox for each test."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.site_dir = self.test_dir / "site"
        self.data_dir = self.site_dir / "src" / "data"
        self.blog_dir = self.site_dir / "src" / "content" / "blog"
        self.reports_dir = self.test_dir / "reports"
        self.snapshots_dir = self.reports_dir / "snapshots"

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.blog_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        # Initialize agent with isolated directories
        self.agent = HeliaAutoEvolutionAgent()
        self.agent.root_dir = self.test_dir
        self.agent.data_dir = self.data_dir
        self.agent.blog_dir = self.blog_dir
        self.agent.reports_dir = self.reports_dir
        self.agent.snapshots_dir = self.snapshots_dir
        self.agent.proposals_file = self.reports_dir / "evolution_proposals.json"
        self.agent.evolution_file = self.data_dir / "evolution_telemetry.json"
        self.agent.immune_file = self.reports_dir / "immune_memory.json"

        self.agent._init_immune_memory()
        self.agent._init_proposals_registry()

        # Create a sample target file
        self.sample_file = self.blog_dir / "test-tool.md"
        self.initial_content = "---\ntitle: Test Tool 2025\nslug: test-tool\n---\nEmpirical review 2025."
        self.sample_file.write_text(self.initial_content, encoding="utf-8")

    def tearDown(self):
        """Clean up temporary test sandbox."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_proposal_creation_and_schema_adherence(self):
        """Verifies proposal data structure strictly adheres to the requested JSON schema."""
        prop = self.agent.create_proposal(
            target_type="article",
            target_slug="test-tool",
            problem="Article has outdated 2025 benchmark claims.",
            evidence=[
                {
                    "type": "source",
                    "url": "file:///site/src/content/blog/test-tool.md",
                    "observedAt": "2026-11-06T00:00:00Z",
                    "value": "Contains 2025 temporal reference"
                }
            ],
            proposed_change="Update to current November 2026 empirical standard with citations.",
            expected_impact="Maintains high credibility and audit conformity.",
            risk_level="medium",
            required_reviews=["AnalystAgent", "PublisherAgent"],
            target_file="site/src/content/blog/test-tool.md"
        )

        self.assertTrue(prop["id"].startswith("evo_"))
        self.assertEqual(prop["status"], "awaiting_review")
        self.assertEqual(prop["target"]["type"], "article")
        self.assertEqual(prop["target"]["slug"], "test-tool")
        self.assertEqual(prop["riskLevel"], "medium")
        self.assertIn("AnalystAgent", prop["requiredReviews"])
        self.assertIn("PublisherAgent", prop["requiredReviews"])
        self.assertIsNone(prop["beforeSnapshot"])
        self.assertIsNone(prop["rollbackReason"])
        self.assertIn("auditLog", prop)
        self.assertTrue(len(prop["auditLog"]) >= 1)

    def test_evidence_sufficiency_rule_blocks_low_traffic_only(self):
        """Verifies rule: low traffic alone is strictly NOT sufficient evidence for editorial modification."""
        prop = self.agent.create_proposal(
            target_type="article",
            target_slug="low-traffic-tool",
            problem="Low pageviews observed over last 7 days.",
            evidence=[
                {
                    "type": "analytics",
                    "url": "https://heliatech.online/blog/low-traffic-tool",
                    "observedAt": "2026-11-06T00:00:00Z",
                    "value": "Views dropped by 45%"
                }
            ],
            proposed_change="Rewrite headline and rewrite editorial score.",
            expected_impact="Attempt to increase clicks.",
            risk_level="medium"
        )

        # Must be blocked in draft status due to lack of verified primary source
        self.assertEqual(prop["status"], "draft")
        self.assertIsNotNone(prop.get("blockedReason"))
        self.assertIn("BLOCKED_INSUFFICIENT_EVIDENCE", prop["blockedReason"])

    def test_mandatory_agent_review_gating(self):
        """Verifies proposal cannot be approved if required agent reviews are missing or rejected."""
        prop = self.agent.create_proposal(
            target_type="link",
            target_slug="apollo-redirect",
            problem="Orphan link target",
            evidence=[{"type": "link_check", "url": "test", "value": "404"}],
            proposed_change="Add 302 redirect",
            expected_impact="Fix dead link",
            risk_level="low",
            required_reviews=["LinkDoctorAgent", "SecurityAgent"],
            target_file="site/src/content/blog/test-tool.md"
        )

        prop_id = prop["id"]
        # Review 1 of 2: LinkDoctorAgent approves
        self.agent.review_proposal(prop_id, reviewer="LinkDoctorAgent", decision="APPROVED", comment="URL valid.")
        updated = self.agent.get_proposal(prop_id)
        self.assertEqual(updated["status"], "awaiting_review")  # SecurityAgent still missing

        # Review 2 of 2: SecurityAgent approves
        self.agent.review_proposal(prop_id, reviewer="SecurityAgent", decision="APPROVED", comment="No secrets.")
        updated = self.agent.get_proposal(prop_id)
        self.assertEqual(updated["status"], "approved")  # Low risk with all reviews approved -> approved

    def test_rejection_marks_proposal_rejected(self):
        """Verifies that an agent rejection immediately marks the proposal as 'rejected'."""
        prop = self.agent.create_proposal(
            target_type="article",
            target_slug="test-tool",
            problem="Benchmark update",
            evidence=[{"type": "source", "url": "test", "value": "check"}],
            proposed_change="Change score from 4.2 to 4.9 without primary benchmark",
            expected_impact="Higher score",
            risk_level="medium",
            required_reviews=["AnalystAgent"]
        )

        self.agent.review_proposal(
            prop["id"],
            reviewer="AnalystAgent",
            decision="REJECTED",
            comment="Rejected: claim lacks reproducible benchmark methodology."
        )

        updated = self.agent.get_proposal(prop["id"])
        self.assertEqual(updated["status"], "rejected")

    def test_human_approval_gate_for_medium_high_risk(self):
        """Verifies that medium and high risk proposals require human approval even after all agents approve."""
        prop = self.agent.create_proposal(
            target_type="article",
            target_slug="test-tool",
            problem="Outdated benchmark claims",
            evidence=[{"type": "source", "url": "test", "value": "source verified"}],
            proposed_change="Upgrade temporal anchor to 2026",
            expected_impact="High accuracy",
            risk_level="medium",
            required_reviews=["AnalystAgent", "PublisherAgent"],
            target_file="site/src/content/blog/test-tool.md"
        )
        prop_id = prop["id"]

        # Both agents approve
        self.agent.review_proposal(prop_id, "AnalystAgent", "APPROVED", "Facts verified.")
        self.agent.review_proposal(prop_id, "PublisherAgent", "APPROVED", "Build verified.")

        # Status must STILL be 'awaiting_review' because human sign-off is required for medium risk
        updated = self.agent.get_proposal(prop_id)
        self.assertEqual(updated["status"], "awaiting_review")
        self.assertFalse(updated["humanApproval"]["approved"])

        # Human supervisor approves
        self.agent.approve_human(prop_id, author="ChiefEditor", rationale="Checked and approved.")
        updated = self.agent.get_proposal(prop_id)
        self.assertEqual(updated["status"], "approved")
        self.assertTrue(updated["humanApproval"]["approved"])

    def test_snapshot_creation_and_deployment(self):
        """Verifies that deployment creates an immutable snapshot and updates target file safely."""
        prop = self.agent.create_proposal(
            target_type="article",
            target_slug="test-tool",
            problem="Update 2025 to 2026",
            evidence=[{"type": "source", "url": "test", "value": "source verified"}],
            proposed_change="Upgrade 2025 to 2026",
            expected_impact="Temporal alignment",
            risk_level="low",
            required_reviews=["PublisherAgent"],
            target_file="site/src/content/blog/test-tool.md"
        )
        prop_id = prop["id"]

        self.agent.review_proposal(prop_id, "PublisherAgent", "APPROVED", "Ready.")

        # Deploy
        deployed_prop = self.agent.deploy_proposal(prop_id, deployer="TestRunner")
        self.assertEqual(deployed_prop["status"], "deployed")
        self.assertIsNotNone(deployed_prop["beforeSnapshot"])

        # Check snapshot exists on disk and holds original content
        snapshot_file = self.test_dir / deployed_prop["beforeSnapshot"]
        self.assertTrue(snapshot_file.exists())
        self.assertEqual(snapshot_file.read_text(encoding="utf-8"), self.initial_content)

        # Check target file was mutated to 2026
        mutated_content = self.sample_file.read_text(encoding="utf-8")
        self.assertIn("2026", mutated_content)
        self.assertNotIn("2025", mutated_content)

    def test_security_audit_aborts_on_secret_leak(self):
        """Verifies that an attempt to propose or deploy a change with an embedded API key is blocked."""
        with self.assertRaises(SecurityError):
            self.agent.create_proposal(
                target_type="article",
                target_slug="test-tool",
                problem="Update config",
                evidence=[{"type": "source", "url": "test", "value": "config"}],
                proposed_change="Inject OpenAI key sk-1234567890123456789012345678901234 into article",
                expected_impact="Auth setup",
                risk_level="low",
                required_reviews=["PublisherAgent"],
                target_file="site/src/content/blog/test-tool.md"
            )

        # Verify target file was untouched
        self.assertEqual(self.sample_file.read_text(encoding="utf-8"), self.initial_content)

    def test_deterministic_rollback_restores_snapshot(self):
        """Verifies that rollback completely restores pre-deployment file state bit-by-bit."""
        prop = self.agent.create_proposal(
            target_type="article",
            target_slug="test-tool",
            problem="Update 2025 to 2026",
            evidence=[{"type": "source", "url": "test", "value": "source"}],
            proposed_change="Upgrade 2025 to 2026",
            expected_impact="Accuracy",
            risk_level="low",
            required_reviews=["PublisherAgent"],
            target_file="site/src/content/blog/test-tool.md"
        )
        prop_id = prop["id"]
        self.agent.review_proposal(prop_id, "PublisherAgent", "APPROVED", "Approved.")
        self.agent.deploy_proposal(prop_id, deployer="TestRunner")

        # Verify mutation occurred
        self.assertIn("2026", self.sample_file.read_text(encoding="utf-8"))

        # Execute rollback
        rolled_back_prop = self.agent.rollback_proposal(
            prop_id,
            reason="Regression observed in edge rendering.",
            author="HumanSupervisor"
        )

        self.assertEqual(rolled_back_prop["status"], "rolled_back")
        self.assertEqual(rolled_back_prop["rolledBackBy"], "HumanSupervisor")

        # Verify target file has been 100% restored to original pre-deploy content
        restored_content = self.sample_file.read_text(encoding="utf-8")
        self.assertEqual(restored_content, self.initial_content)


if __name__ == "__main__":
    unittest.main()
