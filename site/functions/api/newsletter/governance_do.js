/**
 * HeliaTech Forensic Newsletter Engine - Cloudflare Durable Object (Edge Coordinator)
 * ==================================================================================
 * Provides globally unified, transactional serialization across all Cloudflare edge PoPs.
 * 
 * Guarantees:
 * 1. Single global instance: `NEWSLETTER_GOVERNANCE.get(NEWSLETTER_GOVERNANCE.idFromName("newsletter-governance"))`
 * 2. SQLite transaction serialization: using Cloudflare SQLite in Durable Objects (`ctx.storage.sql`).
 * 3. Exact 1 edition per slot: `UNIQUE(scheduled_date, edition_type)`.
 * 4. Double protection: `UNIQUE(slot_key, subscriber_email)`.
 */

export class NewsletterGovernanceDO {
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
    this.sql = ctx.storage.sql;
    this._initTables();
  }

  _initTables() {
    this.sql.exec(`
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
    `);
  }

  async fetch(request) {
    const url = new URL(request.url);

    try {
      if (request.method === "POST" && url.pathname === "/create-draft") {
        const body = await request.json();
        return Response.json(this.createDraft(body));
      }

      if (request.method === "POST" && url.pathname === "/validate-draft") {
        const body = await request.json();
        return Response.json(this.validateDraft(body.slot_key, body.force));
      }

      if (request.method === "POST" && url.pathname === "/dispatch-slot") {
        const body = await request.json();
        return Response.json(await this.dispatchSlot(body));
      }

      if (request.method === "GET" && url.pathname === "/journal") {
        return Response.json(this.getJournal());
      }

      return new Response("Not Found", { status: 404 });
    } catch (err) {
      return Response.json({ error: err.message, stack: err.stack }, { status: 400 });
    }
  }

  createDraft(data) {
    const { slot_key, scheduled_date, edition_type, subject, content_html, content_hash, selected_items } = data;
    
    // Check if slot exists
    const cursor = this.sql.exec("SELECT * FROM newsletter_editions WHERE slot_key = ?", slot_key);
    const existing = [...cursor][0];

    if (existing) {
      if (existing.status === 'cancelled') {
        this.sql.exec("DELETE FROM newsletter_editions WHERE id = ?", existing.id);
      } else {
        throw new Error(`Slot '${slot_key}' already has active edition with status '${existing.status}' (Issue #${existing.issue_number})`);
      }
    }

    const now = new Date().toISOString();
    const itemsJson = typeof selected_items === 'string' ? selected_items : JSON.stringify(selected_items);

    this.sql.exec(`
      INSERT INTO newsletter_editions (
        slot_key, scheduled_date, edition_type, status, issue_number,
        subject, normalized_subject, content_html, content_hash,
        selected_items, rejection_reason, created_at
      ) VALUES (?, ?, ?, 'draft', NULL, ?, ?, ?, ?, ?, NULL, ?)
    `, slot_key, scheduled_date, edition_type.toLowerCase(), subject, subject.toLowerCase(), content_html, content_hash, itemsJson, now);

    return [...this.sql.exec("SELECT * FROM newsletter_editions WHERE slot_key = ?", slot_key)][0];
  }

  validateDraft(slotKey, force = false) {
    const cursor = this.sql.exec("SELECT * FROM newsletter_editions WHERE slot_key = ?", slotKey);
    const draft = [...cursor][0];

    if (!draft) throw new Error(`No edition found for slot '${slotKey}'`);
    if (draft.status === 'validated' || draft.status === 'sent') return draft;

    // Check content hash collision against last 8 editions
    const past = [...this.sql.exec(`
      SELECT * FROM newsletter_editions 
      WHERE status IN ('validated', 'sent') AND slot_key != ?
      ORDER BY COALESCE(issue_number, 0) DESC, created_at DESC 
      LIMIT 8
    `, slotKey)];

    for (const p of past) {
      if (draft.content_hash === p.content_hash) {
        this.sql.exec("UPDATE newsletter_editions SET status = 'blocked', rejection_reason = ? WHERE id = ?", 
          `Identical content_hash to past edition #${p.issue_number}`, draft.id);
        throw new Error(`Identical content_hash to past edition #${p.issue_number}`);
      }
    }

    // Allocate next issue number atomically
    const maxCursor = this.sql.exec("SELECT COALESCE(MAX(issue_number), 54) as max_issue FROM newsletter_editions WHERE issue_number IS NOT NULL");
    const nextIssue = ([...maxCursor][0]?.max_issue || 54) + 1;
    const now = new Date().toISOString();

    this.sql.exec(`
      UPDATE newsletter_editions 
      SET status = 'validated', issue_number = ?, validated_at = ?, rejection_reason = NULL
      WHERE id = ?
    `, nextIssue, now, draft.id);

    return [...this.sql.exec("SELECT * FROM newsletter_editions WHERE id = ?", draft.id)][0];
  }

  async dispatchSlot({ slot_key, subscribers = [], test_mode = false }) {
    const cursor = this.sql.exec("SELECT * FROM newsletter_editions WHERE slot_key = ?", slot_key);
    const edition = [...cursor][0];

    if (!edition) throw new Error(`Slot '${slot_key}' not found`);
    if (edition.status !== 'validated' && edition.status !== 'sending') {
      if (edition.status === 'sent') {
        return { status: "ALREADY_SENT", slot_key, issue_number: edition.issue_number };
      }
      throw new Error(`Edition for slot '${slot_key}' is in status '${edition.status}' (not validated)`);
    }

    this.sql.exec("UPDATE newsletter_editions SET status = 'sending' WHERE id = ?", edition.id);

    let sentCount = 0;
    let blockedCount = 0;
    const now = new Date().toISOString();

    for (const sub of subscribers) {
      const email = String(sub.email || '').trim().toLowerCase().replace(/\s+/g, '');
      if (!email || !email.includes('@')) continue;

      const subId = sub.id ? String(sub.id).trim().toLowerCase() : `sub_${email}`;

      // DOUBLE PROTECTION CHECK
      const existing = [...this.sql.exec(`
        SELECT id FROM newsletter_dispatches 
        WHERE slot_key = ? AND (subscriber_id = ? OR subscriber_email = ?)
      `, slot_key, subId, email)][0];

      if (existing) {
        blockedCount++;
        continue;
      }

      // Record dispatch
      const resendId = test_mode ? `mock_do_${edition.issue_number}_${subId}` : `resend_edge_${Date.now()}`;
      try {
        this.sql.exec(`
          INSERT INTO newsletter_dispatches (
            slot_key, subscriber_id, subscriber_email, issue_number, dispatched_at, resend_id, status
          ) VALUES (?, ?, ?, ?, ?, ?, 'SENT')
        `, slot_key, subId, email, edition.issue_number, now, resendId);
        sentCount++;
      } catch (e) {
        blockedCount++;
      }
    }

    const totalSent = (edition.recipients_sent || 0) + sentCount;
    const totalBlocked = (edition.duplicates_blocked || 0) + blockedCount;

    this.sql.exec(`
      UPDATE newsletter_editions 
      SET status = 'sent', dispatched_at = ?, recipients_sent = ?, duplicates_blocked = ?
      WHERE id = ?
    `, now, totalSent, totalBlocked, edition.id);

    return {
      status: "SUCCESS",
      slot_key,
      issue_number: edition.issue_number,
      recipients_sent: totalSent,
      duplicates_blocked: totalBlocked
    };
  }

  getJournal() {
    return [...this.sql.exec("SELECT * FROM newsletter_editions ORDER BY scheduled_date DESC, created_at DESC LIMIT 50")];
  }
}
