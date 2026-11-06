-- ============================================================================
-- HeliaTech Forensic Newsletter Engine - Cloudflare D1 / Durable Object Schema
-- ============================================================================
-- Globally unique ACID tables for distributed Edge execution.
-- Prevents duplicate editions, collisions, and multiple dispatches per recipient.

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

CREATE INDEX IF NOT EXISTS idx_editions_slot_key ON newsletter_editions(slot_key);
CREATE INDEX IF NOT EXISTS idx_dispatches_slot_email ON newsletter_dispatches(slot_key, subscriber_email);
