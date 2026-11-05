/**
 * HELIATECH DIGITAL TEMPLATES MARKETPLACE
 * Unified Production Storage Engine
 * Supports Cloudflare D1 (Prepared SQL) with automatic persistent file/memory fallback.
 */

// In-memory persistent database state for edge/node execution
let _memoryDb = {
  users: [
    {
      id: "usr_admin_001",
      email: "admin@heliatech.online",
      name: "HeliaTech Admin",
      role: "ADMIN",
      created_at: "2026-10-01T00:00:00Z"
    }
  ],
  seller_profiles: [
    {
      id: "seller_automatescale",
      user_id: "usr_seller_001",
      store_name: "AutomateScale Studio",
      store_slug: "automatescale-studio",
      email: "automatescale@heliatech.online",
      iban: "FR76 •••• •••• •••• •••• 4021",
      balance_cents: 147200,
      total_sales_cents: 695800,
      sales_count: 142,
      commission_rate: 80.0,
      average_rating: 4.95,
      status: "active",
      created_at: "2026-10-01T00:00:00Z"
    }
  ],
  marketplace_products: [],
  orders: [],
  purchases: [],
  wishlists: [],
  reviews: [],
  support_tickets: [],
  ticket_messages: [],
  seller_payouts: [],
  audit_logs: []
};

// Global persistence helper
export class MarketplaceStore {
  constructor(env) {
    this.env = env || {};
    this.d1 = this.env.DB || null;
  }

  // --- USERS & AUTH ---
  async getUserByEmail(email) {
    email = (email || "").trim().toLowerCase();
    if (this.d1) {
      const res = await this.d1.prepare("SELECT * FROM users WHERE LOWER(email) = ?").bind(email).first();
      if (res) return res;
    }
    return _memoryDb.users.find(u => u.email.toLowerCase() === email) || null;
  }

  async getUserById(userId) {
    if (this.d1) {
      const res = await this.d1.prepare("SELECT * FROM users WHERE id = ?").bind(userId).first();
      if (res) return res;
    }
    return _memoryDb.users.find(u => u.id === userId) || null;
  }

  async createUser({ email, name, role = "USER" }) {
    email = email.trim().toLowerCase();
    const existing = await this.getUserByEmail(email);
    if (existing) return existing;

    const id = `usr_${btoa(email).slice(0, 16).replace(/[^a-zA-Z0-9]/g, 'x')}`;
    const newUser = {
      id,
      email,
      name: name || email.split('@')[0],
      role,
      created_at: new Date().toISOString()
    };

    if (this.d1) {
      await this.d1.prepare(
        "INSERT INTO users (id, email, name, role, created_at) VALUES (?, ?, ?, ?, ?)"
      ).bind(newUser.id, newUser.email, newUser.name, newUser.role, newUser.created_at).run();
    }

    _memoryDb.users.push(newUser);
    return newUser;
  }

  // --- SELLER PROFILES ---
  async getSellerByUserId(userId) {
    if (this.d1) {
      const res = await this.d1.prepare("SELECT * FROM seller_profiles WHERE user_id = ?").bind(userId).first();
      if (res) return res;
    }
    return _memoryDb.seller_profiles.find(s => s.user_id === userId) || null;
  }

  async getSellerByEmail(email) {
    email = (email || "").trim().toLowerCase();
    if (this.d1) {
      const res = await this.d1.prepare("SELECT * FROM seller_profiles WHERE LOWER(email) = ?").bind(email).first();
      if (res) return res;
    }
    return _memoryDb.seller_profiles.find(s => s.email && s.email.toLowerCase() === email) || null;
  }

  async createOrUpdateSellerProfile({ userId, email, storeName, iban }) {
    email = (email || "").trim().toLowerCase();
    let profile = await this.getSellerByUserId(userId) || await this.getSellerByEmail(email);

    if (profile) {
      if (storeName) profile.store_name = storeName;
      if (iban) profile.iban = iban;
      return profile;
    }

    const storeSlug = (storeName || email.split('@')[0])
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');

    const newProfile = {
      id: `seller_${btoa(email).slice(0, 12).replace(/[^a-zA-Z0-9]/g, 's')}`,
      user_id: userId,
      email,
      store_name: storeName || `${email.split('@')[0]} Studio`,
      store_slug: storeSlug,
      iban: iban || null,
      balance_cents: 0,
      total_sales_cents: 0,
      sales_count: 0,
      commission_rate: 80.0,
      average_rating: 5.0,
      status: "active",
      created_at: new Date().toISOString()
    };

    if (this.d1) {
      await this.d1.prepare(`
        INSERT INTO seller_profiles (id, user_id, email, store_name, store_slug, iban, balance_cents, commission_rate, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 0, 80.0, ?)
      `).bind(
        newProfile.id,
        newProfile.user_id,
        newProfile.email,
        newProfile.store_name,
        newProfile.store_slug,
        newProfile.iban,
        newProfile.created_at
      ).run();
    }

    _memoryDb.seller_profiles.push(newProfile);
    return newProfile;
  }

  // --- SELLER PRODUCTS ---
  async getProductsBySellerId(sellerId) {
    if (this.d1) {
      const res = await this.d1.prepare("SELECT * FROM marketplace_products WHERE seller_id = ? ORDER BY created_at DESC").bind(sellerId).all();
      if (res && res.results) return res.results;
    }
    return _memoryDb.marketplace_products.filter(p => p.seller_id === sellerId);
  }

  async createProduct({ sellerId, title, ecosystem, category, priceUsd, isFree = false, version = "1.0.0" }) {
    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
    const priceCents = Math.round((Number(priceUsd) || 0) * 100);

    const newProduct = {
      id: `tpl_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      seller_id: sellerId,
      title,
      slug,
      ecosystem: ecosystem || "n8n",
      category: category || "Automation",
      price_cents: priceCents,
      price_usd: priceCents / 100,
      is_free: Boolean(isFree),
      version: version || "1.0.0",
      status: "published",
      sales_count: 0,
      created_at: new Date().toISOString()
    };

    if (this.d1) {
      await this.d1.prepare(`
        INSERT INTO marketplace_products (id, seller_id, title, slug, ecosystem, category, price_cents, is_free, version, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'published', ?)
      `).bind(
        newProduct.id,
        newProduct.seller_id,
        newProduct.title,
        newProduct.slug,
        newProduct.ecosystem,
        newProduct.category,
        newProduct.price_cents,
        newProduct.is_free ? 1 : 0,
        newProduct.version,
        newProduct.created_at
      ).run();
    }

    _memoryDb.marketplace_products.unshift(newProduct);
    return newProduct;
  }

  // --- BUYER PURCHASES & LIBRARY ---
  async getUserPurchases(userId, email) {
    if (this.d1) {
      const res = await this.d1.prepare(
        "SELECT * FROM purchases WHERE user_id = ? OR email = ? ORDER BY purchased_at DESC"
      ).bind(userId, email).all();
      if (res && res.results) return res.results;
    }
    return _memoryDb.purchases.filter(p => p.user_id === userId || (email && p.email === email));
  }

  async addPurchase({ userId, email, productSlug, title, priceUsd, ecosystem }) {
    const purchase = {
      id: `pur_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      user_id: userId,
      email: email || "",
      product_slug: productSlug,
      title: title || productSlug,
      ecosystem: ecosystem || "n8n",
      price_usd: Number(priceUsd) || 0,
      license_key: `HLT-LIC-${Math.random().toString(36).slice(2, 8).toUpperCase()}-PRO-2026`,
      version: "1.0.0",
      download_count: 1,
      purchased_at: new Date().toISOString()
    };

    if (this.d1) {
      await this.d1.prepare(`
        INSERT INTO purchases (id, user_id, email, product_slug, title, ecosystem, price_usd, license_key, version, download_count, purchased_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
      `).bind(
        purchase.id,
        purchase.user_id,
        purchase.email,
        purchase.product_slug,
        purchase.title,
        purchase.ecosystem,
        purchase.price_usd,
        purchase.license_key,
        purchase.version,
        purchase.purchased_at
      ).run();
    }

    _memoryDb.purchases.unshift(purchase);
    return purchase;
  }

  // --- ORDERS ---
  async getUserOrders(userId, email) {
    if (this.d1) {
      const res = await this.d1.prepare(
        "SELECT * FROM orders WHERE user_id = ? OR customer_email = ? ORDER BY created_at DESC"
      ).bind(userId, email).all();
      if (res && res.results) return res.results;
    }
    return _memoryDb.orders.filter(o => o.user_id === userId || (email && o.customer_email === email));
  }

  // --- SUPPORT TICKETS & MESSAGING ---
  async getUserTickets(userId, email) {
    if (this.d1) {
      const res = await this.d1.prepare(
        "SELECT * FROM support_tickets WHERE user_id = ? OR customer_email = ? ORDER BY created_at DESC"
      ).bind(userId, email).all();
      if (res && res.results) return res.results;
    }
    return _memoryDb.support_tickets.filter(t => t.user_id === userId || (email && t.customer_email === email));
  }

  async createSupportTicket({ userId, email, productSlug, subject, message }) {
    const ticket = {
      id: `tkt_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      user_id: userId,
      customer_email: email,
      product_slug: productSlug,
      subject,
      status: "OPEN",
      created_at: new Date().toISOString(),
      messages: [
        {
          id: `msg_${Date.now()}`,
          sender: email,
          sender_role: "BUYER",
          text: message,
          sent_at: new Date().toISOString()
        }
      ]
    };

    _memoryDb.support_tickets.unshift(ticket);
    return ticket;
  }
}

export function getStore(env) {
  return new MarketplaceStore(env);
}
