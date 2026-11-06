"""
HeliaTech Forensic Newsletter Engine
====================================
Mission-critical anti-duplication pipeline and strict slot governance.

Guarantees:
1. Strict Slot Key constraint: Exactly ONE edition per slot (e.g. "YYYY-MM-DD:thursday", "YYYY-MM-DD:tuesday").
2. Database-level unique constraint on (scheduled_date, edition_type).
3. Strict Pipeline Separation:
   Planifier -> Créer brouillon -> Générer contenu -> Valider -> Envoyer -> Archiver.
4. The sending job NEVER regenerates content and only retrieves pre-validated editions.
5. Content Repetition Protection:
   - SHA-256 content_hash compared against the 8 previous editions.
   - Normalized subject similarity check (> 85% flagged/blocked).
   - Editorial block cooldown: featureArticleId, versusId, and dealId cannot be reused within 2 editions.
6. Issue numbering: NEVER incremented on draft creation or rejection; ONLY allocated upon validation & slot lock.
7. Double-send Protection: Checks (slot_key + subscriber_id) and (slot_key + subscriber_email).
   Strict UNIQUE constraint in DB ensures maximum 1 email per subscriber per slot.
"""

import os
import re
import json
import sqlite3
import hashlib
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from difflib import SequenceMatcher
from contextlib import contextmanager
from zoneinfo import ZoneInfo

logger = logging.getLogger("Helia-NewsletterEngine")

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"
DB_PATH = DATA_DIR / "newsletter_governance.db"
SUPERVISION_JSON = DATA_DIR / "newsletter_supervision.json"
SITE_SRC_SUPERVISION = ROOT_DIR / "site" / "src" / "data" / "newsletter_supervision.json"
SITE_PUBLIC_SUPERVISION = ROOT_DIR / "site" / "public" / "data" / "newsletter_supervision.json"


class SlotAlreadyReservedError(Exception):
    """Raised when attempting to create an edition for a slot that already exists."""
    pass


class EditionValidationError(Exception):
    """Raised when an edition fails validation (hash collision, subject collision, cooldown)."""
    pass


class NoValidatedEditionError(Exception):
    """Raised when dispatching a slot that has no validated edition."""
    pass


class NewsletterEngine:
    """
    Forensic ACID-compliant Newsletter Governance Engine with persistent SQLite storage.
    """

    def __init__(self, db_path: Optional[Path] = None, export_supervision: bool = True):
        self.db_path = db_path or DB_PATH
        self.export_supervision = export_supervision
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")  # High concurrency & crash safety
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS newsletter_editions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_key TEXT UNIQUE NOT NULL,
                scheduled_date TEXT NOT NULL,
                edition_type TEXT NOT NULL,
                status TEXT NOT NULL,
                issue_number INTEGER UNIQUE,
                subject TEXT NOT NULL,
                normalized_subject TEXT NOT NULL,
                content_html TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                selected_items TEXT NOT NULL,
                rejection_reason TEXT,
                recipients_total INTEGER DEFAULT 0,
                recipients_sent INTEGER DEFAULT 0,
                recipients_ignored INTEGER DEFAULT 0,
                duplicates_blocked INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                validated_at TEXT,
                dispatched_at TEXT,
                UNIQUE(scheduled_date, edition_type)
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS newsletter_dispatches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slot_key TEXT NOT NULL,
                subscriber_id TEXT NOT NULL,
                subscriber_email TEXT NOT NULL,
                issue_number INTEGER NOT NULL,
                dispatched_at TEXT NOT NULL,
                resend_id TEXT,
                status TEXT NOT NULL,
                UNIQUE(slot_key, subscriber_id),
                UNIQUE(slot_key, subscriber_email)
            );
            """)
            conn.commit()

    @staticmethod
    def compute_slot_key(scheduled_date: str, edition_type: str) -> str:
        """
        Computes the canonical slot key.
        e.g. "2026-11-05:thursday" or "2026-11-10:tuesday"
        """
        dt = scheduled_date.strip()
        etype = edition_type.strip().lower()
        if etype not in ("thursday", "tuesday"):
            raise ValueError(f"Invalid edition_type '{etype}'. Must be 'thursday' or 'tuesday'.")
        return f"{dt}:{etype}"

    @staticmethod
    def is_dispatch_window_open(dt: Optional[datetime] = None) -> Tuple[bool, str]:
        """
        Validates if current or provided datetime falls within the official B2B broadcast window:
        - Tuesday or Thursday in America/New_York timezone
        - Scheduled around 09:00 AM America/New_York (window: 08:30 to 12:00 PM America/New_York).
        Returns: (is_open: bool, message: str)
        """
        ny_tz = ZoneInfo("America/New_York")
        if dt is None:
            ny_now = datetime.now(ny_tz)
        else:
            if dt.tzinfo is None:
                ny_now = dt.replace(tzinfo=ny_tz)
            else:
                ny_now = dt.astimezone(ny_tz)

        weekday = ny_now.weekday()
        day_name = ny_now.strftime("%A")
        time_str = ny_now.strftime("%H:%M %Z")

        if weekday not in (1, 3):  # 1 = Tuesday, 3 = Thursday
            return False, f"Today is {day_name} ({time_str}). Broadcast only permitted on Tuesday or Thursday."

        # Target 09:00 AM America/New_York window (08:30 - 12:00)
        decimal_hour = ny_now.hour + (ny_now.minute / 60.0)
        if decimal_hour < 8.5 or decimal_hour > 12.0:
            return False, f"Outside 09:00 America/New_York window ({time_str}). Permitted window: 08:30 - 12:00 NY."

        return True, f"Window OPEN: {day_name} {time_str} (09:00 America/New_York Broadcast Window)"

    @staticmethod
    def normalize_html_content(text: str) -> str:
        """
        Robust content normalization for duplicate detection:
        1. Strips dynamic personalization tokens: {{email}}, {{unsubscribe_url}}, etc.
        2. Strips issue number variations (#054, ISSUE #..., etc.) to prevent cosmetic renumbering evasion.
        3. Strips URL query tracking parameters (utm_*, ref, via, fpr, timestamps).
        4. Strips HTML markup tags.
        5. Strips punctuation variations and collapses all whitespace into lowercase tokens.
        """
        # Remove template/personalization tokens
        clean = re.sub(r"\{\{[^}]+\}\}", " ", text)
        # Remove issue numbering variations
        clean = re.sub(r"#[0-9]{3,4}", " ", clean)
        clean = re.sub(r"issue\s*#?[0-9]+", " ", clean, flags=re.IGNORECASE)
        # Strip URL query parameters (tracking, UTMs, referral IDs)
        clean = re.sub(r"\?[\w=&_.\-%]+", " ", clean)
        # Strip HTML tags
        clean = re.sub(r"<[^>]+>", " ", clean)
        # Strip punctuation variations
        clean = re.sub(r"[^\w\s]", " ", clean)
        # Collapse whitespace & lowercase
        collapsed = re.sub(r"\s+", " ", clean).strip().lower()
        return collapsed

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Alias for backward compatibility with existing callers."""
        return cls.normalize_html_content(text)

    @classmethod
    def compute_content_hash(cls, subject: str, body_html: str, selected_items: Dict[str, Any]) -> str:
        """
        Computes deterministic SHA-256 hash:
        - Normalized subject (stripped of issue numbers and punctuation)
        - Normalized body HTML (stripped of tags, tokens, tracking query params)
        - Sorted and canonicalized editorial blocks (keys & values sorted, whitespace stripped, lowercased)
        """
        norm_subj = cls.normalize_html_content(subject)
        norm_body = cls.normalize_html_content(body_html)

        # Canonicalize editorial blocks: strictly sorted keys, lowercased stripped string values
        canonical_items = {}
        for k in sorted(selected_items.keys()):
            val = selected_items[k]
            canonical_items[str(k).strip().lower()] = str(val).strip().lower() if val is not None else ""

        items_str = json.dumps(canonical_items, sort_keys=True, separators=(",", ":"))
        payload = f"{norm_subj}__HELIA_DELIM__{norm_body}__HELIA_DELIM__{items_str}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # =========================================================================
    # Step 1: PLANIFIER & STEP 2: CRÉER UN BROUILLON UNIQUE
    # =========================================================================

    def create_draft(
        self,
        scheduled_date: str,
        edition_type: str,
        subject: str,
        body_html: str,
        selected_items: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Creates an atomic unique draft for a specific slot.
        Fails if a draft or edition already exists for this slot.
        Does NOT assign an issue_number.
        """
        slot_key = self.compute_slot_key(scheduled_date, edition_type)
        norm_subj = self.normalize_text(subject)
        content_hash = self.compute_content_hash(subject, body_html, selected_items)
        now_iso = datetime.now().isoformat()
        items_json = json.dumps(selected_items, ensure_ascii=False)

        with self._get_connection() as conn:
            # Check existing edition for this slot
            existing = conn.execute(
                "SELECT * FROM newsletter_editions WHERE slot_key = ?",
                (slot_key,)
            ).fetchone()

            if existing:
                if existing["status"] == "cancelled":
                    # If previously cancelled, replace it cleanly
                    conn.execute("DELETE FROM newsletter_editions WHERE id = ?", (existing["id"],))
                else:
                    raise SlotAlreadyReservedError(
                        f"Slot '{slot_key}' already has an active edition with status '{existing['status']}' (ID: {existing['id']})."
                    )

            try:
                cursor = conn.execute("""
                INSERT INTO newsletter_editions (
                    slot_key, scheduled_date, edition_type, status, issue_number,
                    subject, normalized_subject, content_html, content_hash,
                    selected_items, rejection_reason, created_at
                ) VALUES (?, ?, ?, 'draft', NULL, ?, ?, ?, ?, ?, NULL, ?)
                """, (
                    slot_key, scheduled_date, edition_type.lower(),
                    subject, norm_subj, body_html, content_hash,
                    items_json, now_iso
                ))
                conn.commit()
                edition_id = cursor.lastrowid
            except sqlite3.IntegrityError as e:
                raise SlotAlreadyReservedError(f"Unique slot constraint violated for '{slot_key}': {e}")

        logger.info(f"Created unique draft #{edition_id} for slot '{slot_key}' (hash: {content_hash[:12]}...)")
        self.export_supervision_journal()
        return self.get_edition_by_slot(slot_key)

    # =========================================================================
    # Step 3: VALIDER LE BROUILLON (PROTECTION CONTRE LA RÉPÉTITION)
    # =========================================================================

    def validate_draft(self, slot_key: str, force_human_override: bool = False) -> Dict[str, Any]:
        """
        Validates an existing draft:
        1. Compares content_hash against the last 8 validated/sent editions.
        2. Compares subject similarity against the last 8 editions (flags > 85%).
        3. Prevents re-use of featureArticleId, versusId, dealId in the last 2 editions.
        4. If passed: assigns the next issue_number and sets status = 'validated'.
        5. If failed: marks status = 'blocked' with rejection_reason.
        """
        with self._get_connection() as conn:
            draft = conn.execute(
                "SELECT * FROM newsletter_editions WHERE slot_key = ?",
                (slot_key,)
            ).fetchone()

            if not draft:
                raise ValueError(f"No edition found for slot '{slot_key}'.")

            if draft["status"] in ("validated", "sent"):
                logger.info(f"Slot '{slot_key}' is already {draft['status']} (Issue #{draft['issue_number']}).")
                return dict(draft)

            if draft["status"] not in ("draft", "blocked"):
                raise ValueError(f"Edition for '{slot_key}' cannot be validated from status '{draft['status']}'.")

            # Fetch the last 8 validated/sent editions for content repetition checks
            past_editions = conn.execute("""
                SELECT * FROM newsletter_editions 
                WHERE status IN ('validated', 'sent') AND slot_key != ?
                ORDER BY COALESCE(issue_number, 0) DESC, created_at DESC
                LIMIT 8
            """, (slot_key,)).fetchall()

            # 1. Content Hash Exact Match (8 editions)
            for past in past_editions:
                if draft["content_hash"] == past["content_hash"]:
                    reason = f"Identical content_hash to past edition #{past['issue_number']} ({past['slot_key']}). Refused."
                    self._mark_blocked(conn, draft["id"], reason)
                    raise EditionValidationError(reason)

            # 2. Subject Similarity Check (8 editions)
            draft_norm_subj = draft["normalized_subject"]
            for past in past_editions:
                past_norm_subj = past["normalized_subject"]
                ratio = SequenceMatcher(None, draft_norm_subj, past_norm_subj).ratio()
                if ratio >= 0.85 and not force_human_override:
                    reason = f"Subject similarity {ratio:.1%} exceeds threshold (85%) with #{past['issue_number']} ('{past['subject']}'). Refused."
                    self._mark_blocked(conn, draft["id"], reason)
                    raise EditionValidationError(reason)

            # 3. Item Cooldown Check (last 2 editions)
            draft_items = json.loads(draft["selected_items"])
            recent_2 = past_editions[:2]
            for past in recent_2:
                past_items = json.loads(past["selected_items"])
                for block_key in ("featureArticleId", "versusId", "dealId"):
                    draft_val = draft_items.get(block_key)
                    past_val = past_items.get(block_key)
                    if draft_val and past_val and draft_val == past_val and not force_human_override:
                        reason = f"Editorial block '{block_key}={draft_val}' reused within 2 editions (previously in #{past['issue_number']} {past['slot_key']}). Refused."
                        self._mark_blocked(conn, draft["id"], reason)
                        raise EditionValidationError(reason)

            # All checks PASSED -> Assign Issue Number atomically
            max_row = conn.execute(
                "SELECT COALESCE(MAX(issue_number), 54) as max_issue FROM newsletter_editions WHERE issue_number IS NOT NULL"
            ).fetchone()
            next_issue = max_row["max_issue"] + 1

            now_iso = datetime.now().isoformat()
            conn.execute("""
                UPDATE newsletter_editions
                SET status = 'validated',
                    issue_number = ?,
                    validated_at = ?,
                    rejection_reason = NULL
                WHERE id = ?
            """, (next_issue, now_iso, draft["id"]))
            conn.commit()

        logger.info(f"Validated edition for slot '{slot_key}' -> Assigned ISSUE #{next_issue:03d}")
        self.export_supervision_journal()
        return self.get_edition_by_slot(slot_key)

    def _mark_blocked(self, conn: sqlite3.Connection, edition_id: int, reason: str):
        conn.execute("""
            UPDATE newsletter_editions
            SET status = 'blocked',
                rejection_reason = ?
            WHERE id = ?
        """, (reason, edition_id))
        conn.commit()
        logger.warning(f"Edition #{edition_id} BLOCKED: {reason}")
        self.export_supervision_journal()

    # =========================================================================
    # Step 4: ENVOYER (NEVER REGENERATES CONTENT, ENFORCES DOUBLE PROTECTION)
    # =========================================================================

    def dispatch_slot(
        self,
        slot_key: str,
        test_mode: bool = False,
        subscribers: Optional[List[Dict[str, Any]]] = None,
        resend_sender_fn: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Dispatches a pre-validated edition for a slot.
        - Fails cleanly if no validated edition exists (NEVER creates a new edition).
        - Enforces (slot_key + subscriber_id) / (slot_key + subscriber_email) double protection.
        - Exactly 1 email maximum per subscriber per slot.
        """
        with self._get_connection() as conn:
            edition = conn.execute(
                "SELECT * FROM newsletter_editions WHERE slot_key = ?",
                (slot_key,)
            ).fetchone()

            if not edition:
                raise NoValidatedEditionError(f"No edition found for slot '{slot_key}'. Dispatch aborted.")

            if edition["status"] != "validated" and edition["status"] != "sending":
                if edition["status"] == "sent":
                    logger.info(f"Slot '{slot_key}' already dispatched (Issue #{edition['issue_number']}).")
                    return {
                        "status": "ALREADY_SENT",
                        "slot_key": slot_key,
                        "issue_number": edition["issue_number"],
                        "recipients_sent": edition["recipients_sent"],
                        "duplicates_blocked": edition["duplicates_blocked"]
                    }
                raise NoValidatedEditionError(
                    f"Edition for '{slot_key}' is in status '{edition['status']}' (not validated). Dispatch aborted."
                )

            # Mark sending
            conn.execute(
                "UPDATE newsletter_editions SET status = 'sending' WHERE id = ?",
                (edition["id"],)
            )
            conn.commit()

        # Load subscribers if not provided
        if subscribers is None:
            subscribers = self._load_subscribers()

        sent_count = 0
        blocked_count = 0
        ignored_count = 0
        now_iso = datetime.now().isoformat()
        issue_num = edition["issue_number"]
        subject = edition["subject"]
        body_html = edition["content_html"]

        with self._get_connection() as conn:
            for sub in subscribers:
                # 1. Strict email normalization: remove all whitespace, convert to lowercase
                raw_email = sub.get("email") or ""
                sub_email = re.sub(r"\s+", "", str(raw_email)).strip().lower()

                if not sub_email or "@" not in sub_email:
                    ignored_count += 1
                    continue

                # 2. Strict non-null deterministic subscriber_id: guaranteed never empty, never None
                raw_id = sub.get("id")
                if raw_id and str(raw_id).strip() and str(raw_id).strip().lower() != "none":
                    sub_id = re.sub(r"\s+", "", str(raw_id)).strip().lower()
                else:
                    # Deterministic fallback based on canonical email SHA-256
                    sub_id = f"sub_{hashlib.sha256(sub_email.encode('utf-8')).hexdigest()[:16]}"

                # DOUBLE-PROTECTION CHECK: (slot_key + subscriber_id) or (slot_key + subscriber_email)
                existing = conn.execute("""
                    SELECT id FROM newsletter_dispatches 
                    WHERE slot_key = ? AND (subscriber_id = ? OR subscriber_email = ?)
                """, (slot_key, sub_id, sub_email)).fetchone()

                if existing:
                    blocked_count += 1
                    logger.info(f"BLOCKED DUPLICATE: subscriber '{sub_email}' (id: '{sub_id}') already received slot '{slot_key}'.")
                    continue

                # Execute dispatch
                resend_id = None
                if test_mode:
                    resend_id = f"mock_resend_{issue_num}_{hashlib.md5(sub_email.encode()).hexdigest()[:8]}"
                elif resend_sender_fn:
                    resend_id = resend_sender_fn(sub_email, subject, body_html)
                else:
                    # Simulated success in unit testing environment if no external caller
                    resend_id = f"sim_{issue_num}_{sub_id}"

                if resend_id:
                    try:
                        conn.execute("""
                            INSERT INTO newsletter_dispatches (
                                slot_key, subscriber_id, subscriber_email, issue_number,
                                dispatched_at, resend_id, status
                            ) VALUES (?, ?, ?, ?, ?, ?, 'SENT')
                        """, (slot_key, sub_id, sub_email, issue_num, now_iso, resend_id))
                        conn.commit()
                        sent_count += 1
                    except sqlite3.IntegrityError:
                        blocked_count += 1
                        logger.warning(f"DB blocked race-condition duplicate for subscriber '{sub_email}' on '{slot_key}'.")
                else:
                    ignored_count += 1

            # Mark sent / archived
            total_sent = edition["recipients_sent"] + sent_count
            total_blocked = edition["duplicates_blocked"] + blocked_count
            total_ignored = edition["recipients_ignored"] + ignored_count
            total_recipients = len(subscribers)

            conn.execute("""
                UPDATE newsletter_editions
                SET status = 'sent',
                    dispatched_at = ?,
                    recipients_total = ?,
                    recipients_sent = ?,
                    duplicates_blocked = ?,
                    recipients_ignored = ?
                WHERE id = ?
            """, (
                now_iso, total_recipients, total_sent, total_blocked, total_ignored, edition["id"]
            ))
            conn.commit()

        logger.info(f"Dispatched slot '{slot_key}' Issue #{issue_num:03d}: {sent_count} sent, {blocked_count} duplicates blocked, {ignored_count} ignored.")
        self.export_supervision_journal()
        return {
            "status": "SUCCESS",
            "slot_key": slot_key,
            "issue_number": issue_num,
            "recipients_sent": total_sent,
            "duplicates_blocked": total_blocked,
            "recipients_ignored": total_ignored
        }

    # =========================================================================
    # Step 5: ANNULER UN BROUILLON / ARCHIVER
    # =========================================================================

    def cancel_edition(self, slot_key: str, reason: str = "Cancelled by supervisor") -> Dict[str, Any]:
        """Cancels a draft or validated edition before dispatch. Releases slot."""
        with self._get_connection() as conn:
            edition = conn.execute(
                "SELECT * FROM newsletter_editions WHERE slot_key = ?",
                (slot_key,)
            ).fetchone()

            if not edition:
                raise ValueError(f"No edition found for slot '{slot_key}'.")

            if edition["status"] == "sent":
                raise ValueError(f"Cannot cancel edition for slot '{slot_key}' because it is already sent.")

            conn.execute("""
                UPDATE newsletter_editions
                SET status = 'cancelled',
                    rejection_reason = ?,
                    issue_number = NULL
                WHERE id = ?
            """, (reason, edition["id"]))
            conn.commit()

        logger.info(f"Cancelled edition for slot '{slot_key}': {reason}")
        self.export_supervision_journal()
        return self.get_edition_by_slot(slot_key)

    # =========================================================================
    # QUERY & JOURNAL DE SUPERVISION
    # =========================================================================

    def get_edition_by_slot(self, slot_key: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM newsletter_editions WHERE slot_key = ?",
                (slot_key,)
            ).fetchone()
            return dict(row) if row else None

    def list_editions(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM newsletter_editions 
                ORDER BY scheduled_date DESC, created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def _load_subscribers(self) -> List[Dict[str, Any]]:
        subs_file = DATA_DIR / "subscribers_ledger.json"
        if subs_file.exists():
            try:
                data = json.loads(subs_file.read_text(encoding="utf-8"))
                return data.get("subscribers", [])
            except Exception as e:
                logger.error(f"Error loading subscribers: {e}")
        return [{"id": "sub_dir", "email": "director@heliatech.online"}]

    def export_supervision_journal(self) -> Dict[str, Any]:
        """
        Exports the comprehensive supervision journal to JSON for Sentinel dashboard.
        Saves to:
        - data/newsletter_supervision.json
        - site/src/data/newsletter_supervision.json
        - site/public/data/newsletter_supervision.json
        """
        editions = self.list_editions(limit=25)
        journal = []

        for ed in editions:
            items = {}
            try:
                items = json.loads(ed["selected_items"])
            except Exception:
                pass

            journal.append({
                "id": ed["id"],
                "slot_key": ed["slot_key"],
                "scheduled_date": ed["scheduled_date"],
                "edition_type": ed["edition_type"],
                "issue_number": f"#{ed['issue_number']:03d}" if ed["issue_number"] else "Non assigné (brouillon)",
                "issue_number_raw": ed["issue_number"],
                "status": ed["status"],
                "subject": ed["subject"],
                "content_hash": ed["content_hash"],
                "content_hash_short": ed["content_hash"][:16] + "...",
                "rejection_reason": ed["rejection_reason"],
                "selected_items": items,
                "recipients_total": ed["recipients_total"],
                "recipients_sent": ed["recipients_sent"],
                "recipients_ignored": ed["recipients_ignored"],
                "duplicates_blocked": ed["duplicates_blocked"],
                "created_at": ed["created_at"],
                "validated_at": ed["validated_at"],
                "dispatched_at": ed["dispatched_at"]
            })

        supervision_data = {
            "updated_at": datetime.now().isoformat(),
            "engine_version": "HeliaTech Forensic Newsletter Engine v2.0 (Anti-Duplicate)",
            "total_tracked_editions": len(journal),
            "journal": journal
        }

        if not self.export_supervision:
            return supervision_data

        # Write to all target locations
        for p in (SUPERVISION_JSON, SITE_SRC_SUPERVISION, SITE_PUBLIC_SUPERVISION):
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps(supervision_data, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception as e:
                logger.error(f"Error saving supervision journal to {p}: {e}")

        return supervision_data
