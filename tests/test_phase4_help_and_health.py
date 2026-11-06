#!/usr/bin/env python3
"""
tests/test_phase4_help_and_health.py
Tests de validation pour la Phase 4 de Sentinel Admin :
- Matrice de santé globale consolidée (lecture seule stricte)
- Contrôle d'accès rôle (owner/operator autorisé, guest/unauth rejeté)
- Absence totale de mutation ou de simulation de données
- Intégrité des fiches et concepts du Centre d'Aide Patron
"""

import unittest
import json
import os
import re

class TestPhase4HelpAndHealth(unittest.TestCase):
    def setUp(self):
        self.health_js_path = os.path.join("site", "functions", "api", "sentinel", "health.js")
        self.admin_astro_path = os.path.join("site", "src", "pages", "sentinel", "admin.astro")

    def test_health_endpoint_file_exists(self):
        """Vérifie que l'endpoint Cloudflare /api/sentinel/health est bien présent."""
        self.assertTrue(os.path.exists(self.health_js_path), "health.js doit exister dans functions/api/sentinel/")

    def test_health_endpoint_security_and_auth(self):
        """Vérifie que l'endpoint de santé exige une authentification et bloque les non-administrateurs."""
        with open(self.health_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Contrôle d'accès
        self.assertIn("actorRole !== \"owner\"", content)
        self.assertIn("actorRole !== \"operator\"", content)
        self.assertIn("status: 403", content)

    def test_health_endpoint_strictly_read_only(self):
        """Vérifie que l'endpoint de santé ne contient aucune écriture (INSERT, UPDATE, DELETE)."""
        with open(self.health_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Interdiction formelle d'écriture
        self.assertNotIn("INSERT INTO", content.upper(), "health.js ne doit jamais exécuter d'INSERT")
        self.assertNotIn("UPDATE ", content.upper(), "health.js ne doit jamais exécuter d'UPDATE")
        self.assertNotIn("DELETE FROM", content.upper(), "health.js ne doit jamais exécuter de DELETE")
        self.assertNotIn("DROP TABLE", content.upper(), "health.js ne doit jamais exécuter de DROP")

    def test_health_endpoint_covers_all_six_subsystems(self):
        """Vérifie que les 6 sous-systèmes majeurs sont couverts par le diagnostic."""
        with open(self.health_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_subsystems = [
            "d1_database",
            "r2_storage",
            "fleet_agents",
            "newsletter_system",
            "partner_deals",
            "edge_zero_trust"
        ]
        for sub in required_subsystems:
            self.assertIn(sub, content, f"Le composant {sub} doit être audité par health.js")

    def test_admin_astro_includes_phase4_components(self):
        """Vérifie que admin.astro intègre les 5 panneaux du Centre d'Aide Patron."""
        with open(self.admin_astro_path, "r", encoding="utf-8") as f:
            content = f.read()

        panels = [
            'id="panel-tab-health"',
            'id="panel-tab-routine"',
            'id="panel-tab-glossary"',
            'id="panel-tab-agents"',
            'id="panel-tab-runbooks"'
        ]
        for p in panels:
            self.assertIn(p, content, f"Le panneau {p} doit être présent dans admin.astro")

        # Fonctions JS associées
        self.assertIn("function switchHelpTab", content)
        self.assertIn("async function fetchHealth", content)
        self.assertIn("function filterGlossary", content)
        self.assertIn("function filterHelpAgents", content)

    def test_no_raw_secrets_exposed_in_health_or_help(self):
        """Vérifie qu'aucun secret brut ou token n'est divulgué dans health.js ou admin.astro."""
        with open(self.health_js_path, "r", encoding="utf-8") as f:
            health_content = f.read()
        
        with open(self.admin_astro_path, "r", encoding="utf-8") as f:
            admin_content = f.read()

        sensitive_patterns = [
            r"CLOUDFLARE_D1_TOKEN\s*=\s*['\"][a-zA-Z0-9_\-]+['\"]",
            r"AUDIT_CHECKPOINT_SIGNING_KEY\s*=\s*['\"][a-zA-Z0-9_\-]+['\"]",
            r"TELEGRAM_BOT_TOKEN\s*=\s*['\"][a-zA-Z0-9_\-]+['\"]"
        ]
        for pat in sensitive_patterns:
            self.assertIsNone(re.search(pat, health_content), f"Fuite de secret détectée dans health.js avec le motif {pat}")
            self.assertIsNone(re.search(pat, admin_content), f"Fuite de secret détectée dans admin.astro avec le motif {pat}")

if __name__ == "__main__":
    unittest.main()
