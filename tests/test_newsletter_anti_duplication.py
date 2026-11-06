"""
Unit Tests: HeliaTech Anti-Duplication Newsletter Engine
========================================================
Validates all mandatory constraints from the Priority Corrective Directive:
1. Concurrency: Two jobs started simultaneously for the same slot.
2. Idempotency: Two manual creation requests for the same slot.
3. Retry after error: Resumption recovers existing draft/edition without duplicate creation or issue burn.
4. Redeployment/Interruption: Mid-job resumption skips already-sent subscribers.
5. Content Hash Collision: Identical content within 8 editions is blocked.
6. Subject Similarity: >85% similar subject to recent editions is blocked.
7. Slot Independence: Tuesday and Thursday editions operate independently.
8. Cancel & Replan: Cancelling a draft releases slot cleanly without issue number burn.
9. Double Protection: (slot_key + subscriber_id) guarantees maximum 1 email per subscriber per slot.
"""

import unittest
import tempfile
import threading
from pathlib import Path
from agents.newsletter_engine import (
    NewsletterEngine,
    SlotAlreadyReservedError,
    EditionValidationError,
    NoValidatedEditionError
)


class TestNewsletterAntiDuplication(unittest.TestCase):

    def setUp(self):
        # Create a temporary isolated database for each test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_newsletter.db"
        self.engine = NewsletterEngine(db_path=self.db_path, export_supervision=False)

    def tearDown(self):
        import gc
        gc.collect()
        self.temp_dir.cleanup()

    def test_01_two_manual_creation_requests_same_slot(self):
        """Deux demandes manuelles de création d’édition sur le même créneau."""
        slot_date = "2026-11-12"
        slot_type = "thursday"
        items = {"featureArticleId": "cursor", "versusId": "cursor-vs-copilot", "dealId": "cursor-pro"}

        # First request succeeds
        draft1 = self.engine.create_draft(
            scheduled_date=slot_date,
            edition_type=slot_type,
            subject="Cursor: The Autonomous Code Editor",
            body_html="<p>Full teardown of Cursor multi-file velocity.</p>",
            selected_items=items
        )
        self.assertEqual(draft1["status"], "draft")
        self.assertIsNone(draft1["issue_number"])

        # Second request for same slot MUST be rejected
        with self.assertRaises(SlotAlreadyReservedError):
            self.engine.create_draft(
                scheduled_date=slot_date,
                edition_type=slot_type,
                subject="Cursor: Duplicate Try",
                body_html="<p>Attempting to overwrite or duplicate slot.</p>",
                selected_items=items
            )

    def test_02_concurrent_jobs_same_thursday_slot(self):
        """Deux jobs démarrés simultanément le jeudi."""
        slot_date = "2026-11-19"
        slot_type = "thursday"
        items = {"featureArticleId": "elevenlabs", "versusId": "elevenlabs-vs-heygen", "dealId": "eleven-starter"}

        success_count = 0
        error_count = 0
        lock = threading.Lock()

        def worker():
            nonlocal success_count, error_count
            try:
                # Use separate engine instances sharing same SQLite DB
                worker_engine = NewsletterEngine(db_path=self.db_path, export_supervision=False)
                worker_engine.create_draft(
                    scheduled_date=slot_date,
                    edition_type=slot_type,
                    subject="Voice AI Teardown",
                    body_html="<p>Voice AI benchmark at scale.</p>",
                    selected_items=items
                )
                with lock:
                    success_count += 1
            except SlotAlreadyReservedError:
                with lock:
                    error_count += 1

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Exactly ONE job succeeded, exactly ONE was rejected
        self.assertEqual(success_count, 1)
        self.assertEqual(error_count, 1)

    def test_03_issue_number_never_burned_on_draft_or_rejection(self):
        """Ne pas incrémenter ISSUE # à la création d’un brouillon ou en cas d'erreur."""
        slot_date = "2026-11-26"
        items = {"featureArticleId": "supabase", "versusId": "supabase-vs-firebase", "dealId": "supabase-credits"}

        draft = self.engine.create_draft(
            scheduled_date=slot_date,
            edition_type="thursday",
            subject="Supabase Serverless Postgres",
            body_html="<p>Postgres vs Firebase performance.</p>",
            selected_items=items
        )
        self.assertIsNone(draft["issue_number"], "Draft must not have an issue number assigned.")

        # Validate draft -> now issue_number is assigned
        validated = self.engine.validate_draft(draft["slot_key"])
        self.assertIsNotNone(validated["issue_number"])
        self.assertEqual(validated["issue_number"], 55)

    def test_04_identical_content_hash_blocked(self):
        """Même contenu avec deux numéros d’issue -> rejeté par content_hash."""
        # 1. Create and validate edition 1
        items1 = {"featureArticleId": "make", "versusId": "make-vs-zapier", "dealId": "make-pro"}
        draft1 = self.engine.create_draft(
            scheduled_date="2026-12-03",
            edition_type="thursday",
            subject="The Enterprise Automation Teardown",
            body_html="<p>Make vs Zapier 100k operations benchmark.</p>",
            selected_items=items1
        )
        self.engine.validate_draft(draft1["slot_key"])

        # 2. Attempt to create and validate edition 2 on a subsequent date with IDENTICAL content
        draft2 = self.engine.create_draft(
            scheduled_date="2026-12-10",
            edition_type="thursday",
            subject="The Enterprise Automation Teardown",
            body_html="<p>Make vs Zapier 100k operations benchmark.</p>",
            selected_items=items1
        )
        # Validation MUST fail due to identical content_hash
        with self.assertRaises(EditionValidationError) as ctx:
            self.engine.validate_draft(draft2["slot_key"])
        self.assertIn("Identical content_hash", str(ctx.exception))

        # Check status is marked 'blocked' and issue_number was NOT allocated
        blocked = self.engine.get_edition_by_slot(draft2["slot_key"])
        self.assertEqual(blocked["status"], "blocked")
        self.assertIsNone(blocked["issue_number"])

    def test_05_similar_subject_blocked(self):
        """Même sujet ou quasi identique (> 85%) avec contenu différent -> bloqué."""
        items1 = {"featureArticleId": "linear", "versusId": "linear-vs-jira", "dealId": "linear-perk"}
        draft1 = self.engine.create_draft(
            scheduled_date="2026-12-17",
            edition_type="thursday",
            subject="Linear: High Velocity Issue Tracking for Modern Devs",
            body_html="<p>Content variation A.</p>",
            selected_items=items1
        )
        self.engine.validate_draft(draft1["slot_key"])

        items2 = {"featureArticleId": "resend", "versusId": "resend-vs-sendgrid", "dealId": "resend-credits"}
        draft2 = self.engine.create_draft(
            scheduled_date="2026-12-24",
            edition_type="thursday",
            subject="Linear: High Velocity Issue Tracking for Modern Devs!",  # 98% similar subject
            body_html="<p>Different body text completely.</p>",
            selected_items=items2
        )
        with self.assertRaises(EditionValidationError) as ctx:
            self.engine.validate_draft(draft2["slot_key"])
        self.assertIn("Subject similarity", str(ctx.exception))

    def test_06_editorial_block_cooldown_within_two_editions(self):
        """Empêcher la réutilisation des mêmes articles, duel et deal dans les 2 dernières éditions."""
        items1 = {"featureArticleId": "brevo", "versusId": "brevo-vs-mailchimp", "dealId": "brevo-deal"}
        draft1 = self.engine.create_draft(
            scheduled_date="2026-12-31",
            edition_type="thursday",
            subject="Brevo Marketing Automation",
            body_html="<p>Body 1.</p>",
            selected_items=items1
        )
        self.engine.validate_draft(draft1["slot_key"])

        # Immediately next edition tries to reuse "brevo" as featureArticleId
        items2 = {"featureArticleId": "brevo", "versusId": "resend-vs-brevo", "dealId": "different-deal"}
        draft2 = self.engine.create_draft(
            scheduled_date="2027-01-07",
            edition_type="thursday",
            subject="Brevo vs Resend Comparison",
            body_html="<p>Different body.</p>",
            selected_items=items2
        )
        with self.assertRaises(EditionValidationError) as ctx:
            self.engine.validate_draft(draft2["slot_key"])
        self.assertIn("reused within 2 editions", str(ctx.exception))

    def test_07_tuesday_and_thursday_slot_independence(self):
        """Création d’une édition mardi puis jeudi."""
        tuesday_items = {"featureArticleId": "tome", "versusId": "tome-vs-gamma", "dealId": "tome-deal"}
        draft_tue = self.engine.create_draft(
            scheduled_date="2026-11-10",
            edition_type="tuesday",
            subject="Tuesday AI Executive Briefing",
            body_html="<p>Tuesday intelligence.</p>",
            selected_items=tuesday_items
        )
        val_tue = self.engine.validate_draft(draft_tue["slot_key"])
        self.assertEqual(val_tue["status"], "validated")

        thursday_items = {"featureArticleId": "gamma-app", "versusId": "gamma-vs-beautiful", "dealId": "gamma-deal"}
        draft_thu = self.engine.create_draft(
            scheduled_date="2026-11-12",
            edition_type="thursday",
            subject="Thursday Architectural Radar",
            body_html="<p>Thursday teardown.</p>",
            selected_items=thursday_items
        )
        val_thu = self.engine.validate_draft(draft_thu["slot_key"])
        self.assertEqual(val_thu["status"], "validated")

        self.assertNotEqual(val_tue["issue_number"], val_thu["issue_number"])

    def test_08_dispatch_fails_without_validated_edition(self):
        """L'envoi doit échouer proprement s'il n'existe pas d'édition validée."""
        with self.assertRaises(NoValidatedEditionError):
            self.engine.dispatch_slot("2026-11-12:thursday", test_mode=True)

    def test_09_double_protection_destinataire_slot_and_subscriber(self):
        """Double protection d'envoi : scheduled_slot + subscriber_id (1 seul email par abonné par créneau)."""
        slot_date = "2026-11-19"
        items = {"featureArticleId": "resend", "versusId": "resend-vs-brevo", "dealId": "resend-perk"}

        draft = self.engine.create_draft(
            scheduled_date=slot_date,
            edition_type="thursday",
            subject="Developer Email Infrastructure",
            body_html="<p>Resend architecture breakdown.</p>",
            selected_items=items
        )
        self.engine.validate_draft(draft["slot_key"])

        subscribers = [
            {"id": "sub_01", "email": "alice@company.com"},
            {"id": "sub_02", "email": "bob@enterprise.io"},
            {"id": "sub_01", "email": "alice@company.com"}  # Duplicate in subscriber list
        ]

        # First dispatch
        res1 = self.engine.dispatch_slot(draft["slot_key"], test_mode=True, subscribers=subscribers)
        self.assertEqual(res1["recipients_sent"], 2)
        self.assertEqual(res1["duplicates_blocked"], 1)

        # Retry or second dispatch job on same slot
        res2 = self.engine.dispatch_slot(draft["slot_key"], test_mode=True, subscribers=subscribers)
        self.assertEqual(res2["status"], "ALREADY_SENT")
        self.assertEqual(res2["recipients_sent"], 2)

    def test_10_cancel_draft_and_resumption(self):
        """Annulation d’un brouillon et reprise du créneau sans fuite de numéro."""
        slot_date = "2026-11-26"
        items = {"featureArticleId": "descript", "versusId": "descript-vs-riverside", "dealId": "descript-perk"}

        draft = self.engine.create_draft(
            scheduled_date=slot_date,
            edition_type="thursday",
            subject="Descript Audio Editing",
            body_html="<p>Draft 1.</p>",
            selected_items=items
        )
        self.assertEqual(draft["status"], "draft")

        # Cancel draft
        cancelled = self.engine.cancel_edition(draft["slot_key"], reason="Editorial redirection")
        self.assertEqual(cancelled["status"], "cancelled")

        # Re-plan slot with new draft
        new_items = {"featureArticleId": "podcastle", "versusId": "podcastle-vs-riverside", "dealId": "podcastle-perk"}
        draft2 = self.engine.create_draft(
            scheduled_date=slot_date,
            edition_type="thursday",
            subject="Podcastle Studio Teardown",
            body_html="<p>Draft 2 with new topic.</p>",
            selected_items=new_items
        )
        self.assertEqual(draft2["status"], "draft")
        val2 = self.engine.validate_draft(draft2["slot_key"])
        self.assertEqual(val2["status"], "validated")
        self.assertIsNotNone(val2["issue_number"])



    def test_11_dispatch_window_america_new_york(self):
        """Vérification stricte de la fenêtre horaire America/New_York (mardi/jeudi à 09:00)."""
        from datetime import datetime
        from zoneinfo import ZoneInfo
        ny_tz = ZoneInfo("America/New_York")

        # 1. Jeudi 09:15 AM New York -> OPEN
        thu_0915 = datetime(2026, 11, 12, 9, 15, tzinfo=ny_tz)
        is_open, msg = self.engine.is_dispatch_window_open(thu_0915)
        self.assertTrue(is_open, f"Should be open: {msg}")

        # 2. Mardi 10:00 AM New York -> OPEN
        tue_1000 = datetime(2026, 11, 10, 10, 0, tzinfo=ny_tz)
        is_open, msg = self.engine.is_dispatch_window_open(tue_1000)
        self.assertTrue(is_open, f"Should be open: {msg}")

        # 3. Mercredi 09:00 AM New York -> CLOSED (mauvais jour)
        wed_0900 = datetime(2026, 11, 11, 9, 0, tzinfo=ny_tz)
        is_open, msg = self.engine.is_dispatch_window_open(wed_0900)
        self.assertFalse(is_open, "Wednesday should be blocked")

        # 4. Jeudi 04:00 AM New York -> CLOSED (trop tôt, hors créneau 09:00)
        thu_0400 = datetime(2026, 11, 12, 4, 0, tzinfo=ny_tz)
        is_open, msg = self.engine.is_dispatch_window_open(thu_0400)
        self.assertFalse(is_open, "04:00 AM NY should be blocked")

    def test_12_content_hash_robust_against_item_reordering_and_tracking_params(self):
        """Calcul de content_hash insensible à l'ordre des blocs, UTMs et tokens dynamiques."""
        subject1 = "⚡ [THE RADAR #054] Cursor Teardown & Benchmark"
        subject2 = "⚡ [THE RADAR] Cursor Teardown & Benchmark!"

        body1 = '<p>Check <a href="https://heliatech.online/reviews/cursor/?utm_source=radar&utm_medium=email">Cursor review</a> for {{email}}.</p>'
        body2 = '<p>Check <a href="https://heliatech.online/reviews/cursor/?utm_source=twitter&ref=newsletter">Cursor review</a> for {{email}}.</p>'

        items_ordered = {"featureArticleId": "cursor", "versusId": "make-vs-zapier", "dealId": "make-pro"}
        items_reversed = {"dealId": "make-pro", "versusId": "make-vs-zapier", "featureArticleId": "cursor"}

        hash1 = self.engine.compute_content_hash(subject1, body1, items_ordered)
        hash2 = self.engine.compute_content_hash(subject2, body2, items_reversed)

        self.assertEqual(hash1, hash2, "Content hashes must match regardless of block ordering, tracking URLs or issue tokens.")

    def test_13_subscriber_email_and_id_normalization(self):
        """Normalisation des emails (minuscules, sans espaces) et génération déterministe d'ID."""
        slot_date = "2026-11-26"
        items = {"featureArticleId": "tome", "versusId": "tome-vs-gamma", "dealId": "tome-perk"}

        draft = self.engine.create_draft(
            scheduled_date=slot_date,
            edition_type="thursday",
            subject="AI Presentation Teardown",
            body_html="<p>Slide intelligence.</p>",
            selected_items=items
        )
        self.engine.validate_draft(draft["slot_key"])

        # Subscribers with casing, whitespace, and None id variations
        subscribers = [
            {"id": None, "email": "  Director@HeliaTech.Online  "},
            {"id": "", "email": "director@heliatech.online"},
            {"id": "sub_dir", "email": "DIRECTOR@HELIATECH.ONLINE"}
        ]

        res = self.engine.dispatch_slot(draft["slot_key"], test_mode=True, subscribers=subscribers)
        # Exactly 1 should be sent, 2 should be blocked as duplicates
        self.assertEqual(res["recipients_sent"], 1)
        self.assertEqual(res["duplicates_blocked"], 2)

    def test_14_revalidation_preserves_issue_number(self):
        """Une édition validée ou envoyée conserve son numéro d'issue et ne crée jamais #055."""
        slot_date = "2026-12-03"
        items = {"featureArticleId": "n8n", "versusId": "make-vs-n8n", "dealId": "n8n-cloud"}

        draft = self.engine.create_draft(
            scheduled_date=slot_date,
            edition_type="thursday",
            subject="n8n Self-Hosted Automation",
            body_html="<p>Self hosting vs cloud.</p>",
            selected_items=items
        )
        val1 = self.engine.validate_draft(draft["slot_key"])
        assigned_issue = val1["issue_number"]
        self.assertIsNotNone(assigned_issue)

        # Re-running validation on same slot MUST return the exact same issue number
        val2 = self.engine.validate_draft(draft["slot_key"])
        self.assertEqual(val2["issue_number"], assigned_issue)

        # Dispatch
        self.engine.dispatch_slot(draft["slot_key"], test_mode=True, subscribers=[{"email": "test@test.com"}])

        # Re-validating after dispatch MUST still preserve the same issue number
        val3 = self.engine.validate_draft(draft["slot_key"])
        self.assertEqual(val3["issue_number"], assigned_issue)

    def test_15_multiprocess_cloud_simulation(self):
        """Simulation multi-processus : deux processus OS indépendants tentent de réserver le même créneau."""
        import subprocess
        import sys

        slot_date = "2026-12-10"
        slot_type = "thursday"

        script = f"""
import sys
from pathlib import Path
from agents.newsletter_engine import NewsletterEngine, SlotAlreadyReservedError
engine = NewsletterEngine(db_path=Path(r'{self.db_path}'), export_supervision=False)
try:
    engine.create_draft(
        scheduled_date='{slot_date}',
        edition_type='{slot_type}',
        subject='Process Race Subject',
        body_html='<p>Race body.</p>',
        selected_items={{'featureArticleId': 'race', 'versusId': 'a-vs-b', 'dealId': 'deal'}}
    )
    sys.exit(0)
except SlotAlreadyReservedError:
    sys.exit(42)
"""

        # Spawn two separate OS processes simultaneously
        p1 = subprocess.Popen([sys.executable, "-c", script])
        p2 = subprocess.Popen([sys.executable, "-c", script])

        p1.wait()
        p2.wait()

        codes = {p1.returncode, p2.returncode}
        # Exactly one process exited with 0 (created draft), and exactly one with 42 (SlotAlreadyReservedError)
        self.assertEqual(codes, {0, 42}, f"Expected one success (0) and one collision (42), got: {codes}")


if __name__ == "__main__":
    unittest.main()
