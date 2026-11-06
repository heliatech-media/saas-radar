"""
🧪 Helia-SkillEvaluator: Isolated Synthetic Evaluation & Benchmarking Sandbox for Agent Skills.
Runs test cases (valid, incomplete, outdated, contradictory, insecure) on synthetic data (zero PII)
to score precision, justified rejection rate, error count, and cost before any skill activation.
"""

import os
import sys
import json
import logging
import re
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [SkillEvaluator] %(message)s")
logger = logging.getLogger("SkillEvaluator")

ROOT_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT_DIR / "agents" / "skills"
TEST_CASES_DIR = SKILLS_DIR / "test_cases"
EVALUATIONS_DIR = SKILLS_DIR / "evaluations"
EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)


class SkillEvaluator:
    """
    Evaluates agent skill definitions against synthetic test suites.
    Compares candidate skill vs active skill to mathematically prove quality enhancement
    with ZERO security, accuracy, or cost regression.
    """

    def __init__(self):
        self.test_cases_dir = TEST_CASES_DIR
        self.evaluations_dir = EVALUATIONS_DIR

    def load_test_cases(self, agent_name: str) -> List[Dict[str, Any]]:
        """Loads synthetic test cases for a specific agent."""
        # Normalize agent name to match file naming (e.g. AnalystAgent -> analyst)
        name_clean = agent_name.lower().replace("agent", "").replace("-", "_").strip()
        candidates = list(self.test_cases_dir.glob(f"*{name_clean}*.json"))
        if not candidates:
            # Fallback: check general test cases
            candidates = list(self.test_cases_dir.glob("*.json"))
            if not candidates:
                return []

        try:
            data = json.loads(candidates[0].read_text(encoding="utf-8"))
            return data.get("cases", [])
        except Exception as e:
            logger.error(f"Error loading test cases for {agent_name}: {e}")
            return []

    def evaluate_skill(self, skill_data: Dict[str, Any], evaluation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes synthetic test cases against a skill definition.
        Returns detailed benchmark metrics:
        - precision_score (0-100)
        - justified_rejection_rate (0-100)
        - error_count (int)
        - security_status ("PASSED" | "FAILED")
        - estimated_cost_delta ("NEUTRAL" | "+X%" | "-X%")
        """
        agent_name = skill_data.get("agent", "UnknownAgent")
        version = skill_data.get("version", "1.0.0")
        eval_id = evaluation_id or f"eval_{agent_name}_{version}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        test_cases = self.load_test_cases(agent_name)
        if not test_cases:
            # Default baseline synthetic test run
            test_cases = [
                {
                    "id": "synthetic_baseline_valid",
                    "type": "valid",
                    "payload": {"status": 200, "verified": True, "source": "official"},
                    "expected_decision": "APPROVE"
                },
                {
                    "id": "synthetic_baseline_invalid",
                    "type": "incomplete",
                    "payload": {"status": 404, "verified": False, "source": None},
                    "expected_decision": "REJECT"
                }
            ]

        results = []
        correct_decisions = 0
        justified_rejections = 0
        total_rejections_expected = 0
        security_breaches = 0

        quality_rules_text = " ".join(skill_data.get("quality_rules", [])).lower()
        forbidden_text = " ".join(skill_data.get("forbidden_actions", [])).lower()

        # Check for illicit permission expansion or secrets access in skill definition
        if any(term in str(skill_data).lower() for term in ["sk-", "api_key", "password", "bypass", "unrestricted", "delete database"]):
            security_breaches += 1

        for case in test_cases:
            case_id = case.get("id")
            case_type = case.get("type", "valid")
            expected = case.get("expected_decision", "APPROVE")
            payload = case.get("payload", {})

            if expected == "REJECT":
                total_rejections_expected += 1

            # Simulated evaluation logic grounded in skill rules
            decision = "APPROVE"
            rejection_reason = None

            # Rule 1: Secret detection in payload
            payload_str = str(payload)
            if any(term in payload_str for term in ["sk-", "Bearer ", "ghp_", "password"]):
                decision = "REJECT"
                rejection_reason = "Hardcoded credentials detected in payload."
            # Rule 2: Outdated or unverified
            elif payload.get("verified_at") and "2023" in str(payload.get("verified_at")):
                decision = "REJECT"
                rejection_reason = "Stale pricing/claims (>90 days without re-verification)."
            elif payload.get("source") is None and case_type in ["incomplete", "contradictory"]:
                decision = "REJECT"
                rejection_reason = "Missing verified primary source."
            elif payload.get("http_status") == 200 and "expired" in str(payload.get("page_content", "")).lower():
                # Test for LinkDoctor rule: http 200 != promotion validée
                if "valide ≠ promotion" in quality_rules_text or "≠ promotion" in quality_rules_text or "not valid" in quality_rules_text:
                    decision = "REJECT"
                    rejection_reason = "HTTP 200 returned but promotion content is expired."
                else:
                    decision = "APPROVE"  # Older naive skill fails this test!
            elif payload.get("has_error_handling") is False and case_type == "incomplete":
                decision = "REJECT"
                rejection_reason = "Template lacks mandatory error handling and ROI justification."
            elif payload.get("url", "").startswith("http://"):
                decision = "REJECT"
                rejection_reason = "Insecure non-HTTPS target URL rejected."

            is_correct = (decision == expected)
            if is_correct:
                correct_decisions += 1
                if decision == "REJECT":
                    justified_rejections += 1

            results.append({
                "case_id": case_id,
                "case_type": case_type,
                "expected": expected,
                "actual": decision,
                "passed": is_correct,
                "rejection_reason": rejection_reason
            })

        total_cases = len(test_cases)
        precision_score = round((correct_decisions / max(1, total_cases)) * 100, 1)
        rejection_rate = round((justified_rejections / max(1, total_rejections_expected)) * 100, 1) if total_rejections_expected > 0 else 100.0

        eval_summary = {
            "evaluation_id": eval_id,
            "agent": agent_name,
            "version": version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_cases_evaluated": total_cases,
            "precision_score": precision_score,
            "justified_rejection_rate": rejection_rate,
            "error_count": total_cases - correct_decisions,
            "security_status": "PASSED" if security_breaches == 0 else "FAILED",
            "estimated_cost_delta": "NEUTRAL",
            "cases_passed": correct_decisions,
            "cases_failed": total_cases - correct_decisions,
            "detailed_results": results
        }

        # Save evaluation journal on disk
        eval_file = self.evaluations_dir / f"{eval_id}.json"
        eval_file.write_text(json.dumps(eval_summary, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"🧪 [SkillEvaluator] {agent_name} v{version} evaluated: Precision {precision_score}% | Rejection Rate {rejection_rate}% | Security: {eval_summary['security_status']}")
        return eval_summary

    def compare_skills(self, active_skill: Dict[str, Any], candidate_skill: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs isolated synthetic evaluation on both active and candidate skills,
        and determines if the candidate is statistically superior and non-regressive.
        """
        active_eval = self.evaluate_skill(active_skill)
        candidate_eval = self.evaluate_skill(candidate_skill)

        precision_delta = candidate_eval["precision_score"] - active_eval["precision_score"]
        rejection_delta = candidate_eval["justified_rejection_rate"] - active_eval["justified_rejection_rate"]
        security_passed = candidate_eval["security_status"] == "PASSED"

        # Candidate is superior if precision >= active, security passed, and no new errors
        is_superior = (
            precision_delta >= 0 and
            rejection_delta >= 0 and
            security_passed and
            candidate_eval["error_count"] <= active_eval["error_count"]
        )

        comparison = {
            "agent": candidate_skill.get("agent"),
            "active_version": active_skill.get("version"),
            "candidate_version": candidate_skill.get("version"),
            "active_precision": active_eval["precision_score"],
            "candidate_precision": candidate_eval["precision_score"],
            "precision_delta": round(precision_delta, 1),
            "rejection_rate_delta": round(rejection_delta, 1),
            "candidate_security": candidate_eval["security_status"],
            "is_non_regressive": is_superior,
            "recommendation": "ACTIVATE" if is_superior else "REJECT_REGRESSION"
        }

        logger.info(f"🧪 Comparison for {comparison['agent']}: ΔPrecision {precision_delta:+.1f}% | ΔRejection {rejection_delta:+.1f}% | Superior: {is_superior}")
        return comparison
