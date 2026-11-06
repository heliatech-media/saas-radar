-- ============================================================================
-- HeliaTech Sentinel Migration 0001 : Schéma Initial
-- ============================================================================
-- Tables fondamentales : subscribers, fleet_controls, owner_approvals, sentinel_audit_logs, newsletter_editions, newsletter_dispatches

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS subscribers (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    role TEXT,
    country TEXT,
    country_code TEXT,
    signup_date TEXT NOT NULL,
    source_path TEXT,
    lead_magnet TEXT,
    status TEXT NOT NULL DEFAULT 'Verified',
    last_engaged_at TEXT,
    unsubscribed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status);

CREATE TABLE IF NOT EXISTS fleet_controls (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    fleet_status TEXT NOT NULL DEFAULT 'RUNNING',
    newsletter_emergency_stop INTEGER NOT NULL DEFAULT 0,
    suspended_agents TEXT NOT NULL DEFAULT '[]',
    exempt_agents TEXT NOT NULL DEFAULT '["SecurityAgent","MarketplaceSecuritySentinel","NotifierAgent"]',
    last_updated_at TEXT NOT NULL,
    last_updated_by TEXT NOT NULL
);

INSERT OR IGNORE INTO fleet_controls (id, fleet_status, newsletter_emergency_stop, suspended_agents, exempt_agents, last_updated_at, last_updated_by)
VALUES (1, 'RUNNING', 0, '[]', '["SecurityAgent","MarketplaceSecuritySentinel","NotifierAgent"]', datetime('now'), 'system_init');

CREATE TABLE IF NOT EXISTS owner_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT NOT NULL,
    item_ref TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    content_payload TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    author_agent TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    created_at TEXT NOT NULL,
    decided_at TEXT,
    decided_by TEXT,
    decision_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_approvals_status ON owner_approvals(status);

CREATE TABLE IF NOT EXISTS sentinel_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    actor_email TEXT NOT NULL,
    actor_role TEXT NOT NULL DEFAULT 'owner',
    action TEXT NOT NULL,
    target TEXT NOT NULL,
    details_json TEXT NOT NULL,
    previous_state TEXT,
    new_state TEXT,
    ip_address TEXT,
    user_agent TEXT,
    signature TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON sentinel_audit_logs(timestamp);

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
    UNIQUE(slot_key, subscriber_email),
    FOREIGN KEY(slot_key) REFERENCES newsletter_editions(slot_key)
);
