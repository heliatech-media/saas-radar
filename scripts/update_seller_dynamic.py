import re

with open('site/src/pages/seller/index.astro', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Header Card elements
content = re.sub(
    r'<img src="https://api\.dicebear\.com/7\.x/identicon/svg\?seed=AutomateScale" alt="AutomateScale" class="w-full h-full rounded-2xl object-cover bg-slate-950" />',
    r'<img id="seller-avatar-img" src="https://api.dicebear.com/7.x/identicon/svg?seed=AutomateScale" alt="Studio Avatar" class="w-full h-full rounded-2xl object-cover bg-slate-950" />',
    content
)

content = re.sub(
    r'<h1 class="text-xl sm:text-2xl font-black text-white">AutomateScale Studio</h1>',
    r'<h1 class="text-xl sm:text-2xl font-black text-white" id="seller-studio-name">AutomateScale Studio</h1>',
    content
)

content = re.sub(
    r'<span>automatescale@heliatech\.online</span>\s*<span>•</span>\s*<span class="text-cyan-400">IBAN SEPA •••• 4021 Vérifié</span>',
    r'<span id="seller-email-display">automatescale@heliatech.online</span>\n            <span>•</span>\n            <span id="seller-iban-status" class="text-cyan-400">IBAN SEPA •••• 4021 Vérifié</span>',
    content
)

# Add logout button to top actions if not present
if "id=\"btn-seller-logout\"" not in content:
    content = re.sub(
        r'(<button id="btn-request-payout-top"[^>]*>.*?</button>)',
        r'\1\n        <button id="btn-seller-logout" class="px-3 py-2.5 rounded-xl bg-slate-950 hover:bg-rose-950/40 text-slate-400 hover:text-rose-300 border border-slate-800 text-xs font-mono transition-all">\n          🚪 Déconnexion\n        </button>',
        content,
        flags=re.DOTALL
    )

# 2. Add IDs to KPI metrics
content = re.sub(
    r'<div class="text-2xl sm:text-3xl font-black text-emerald-400 font-mono mb-1">\$5,566\.40</div>',
    r'<div class="text-2xl sm:text-3xl font-black text-emerald-400 font-mono mb-1" id="kpi-seller-revenue">$5,566.40</div>',
    content
)

content = re.sub(
    r'<div class="text-2xl sm:text-3xl font-black text-cyan-400 font-mono mb-1">\$1,472\.00</div>',
    r'<div class="text-2xl sm:text-3xl font-black text-cyan-400 font-mono mb-1" id="kpi-seller-balance">$1,472.00</div>',
    content
)

content = re.sub(
    r'<div class="text-2xl sm:text-3xl font-black text-indigo-400 font-mono mb-1">142</div>',
    r'<div class="text-2xl sm:text-3xl font-black text-indigo-400 font-mono mb-1" id="kpi-seller-sales">142</div>',
    content
)

content = re.sub(
    r'<div class="text-2xl sm:text-3xl font-black text-amber-400 font-mono mb-1">★ 4\.95</div>',
    r'<div class="text-2xl sm:text-3xl font-black text-amber-400 font-mono mb-1" id="kpi-seller-rating">★ 4.95</div>',
    content
)

# 3. Add IDs to tabs & badges
content = re.sub(
    r'<span>📦</span> Mes Produits \(\{sellerBlueprints\.length\}\)',
    r'<span>📦</span> Mes Produits (<span id="badge-seller-prod-count">{sellerBlueprints.length}</span>)',
    content
)

# 4. Add IDs to tables
content = re.sub(
    r'<tbody class="divide-y divide-slate-800/80 text-slate-300">\s*<tr>\s*<td class="py-3 px-4 text-white font-bold">n8n AI Waterfall Lead Enrichment</td>',
    r'<tbody class="divide-y divide-slate-800/80 text-slate-300" id="seller-recent-sales-tbody">\n              <tr>\n                <td class="py-3 px-4 text-white font-bold">n8n AI Waterfall Lead Enrichment</td>',
    content
)

content = re.sub(
    r'<tbody class="divide-y divide-slate-800/80 text-slate-300">\s*\{sellerBlueprints\.map',
    r'<tbody class="divide-y divide-slate-800/80 text-slate-300" id="seller-products-tbody">\n              {sellerBlueprints.map',
    content
)

# 5. Add ID to chart wrapper
content = re.sub(
    r'(<div class="h-44 flex items-end gap-3 sm:gap-6 pt-4 px-2">)',
    r'<div id="seller-chart-container">\n        \1',
    content
)
if '<div id="seller-chart-container">' in content and '</div>\n      </div>\n\n      <!-- Recent Sales (80/20 Breakdown)' not in content:
    content = re.sub(
        r'(<!-- Recent Sales \(80/20 Breakdown\) -->)',
        r'</div>\n      </div>\n\n      \1',
        content,
        count=1
    )

# 6. Add ID to payout box
content = re.sub(
    r'<div class="p-6 rounded-2xl bg-slate-900/40 border border-emerald-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">',
    r'<div class="p-6 rounded-2xl bg-slate-900/40 border border-emerald-500/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4" id="seller-payout-status-box">',
    content
)

# 7. Inject initSellerStudio script
seller_script_injection = """
    // =========================================================================
    // DYNAMIC SELLER STUDIO HYDRATION (Scoped to logged-in seller)
    // =========================================================================
    function initSellerStudio() {
      let session = null;
      try {
        session = JSON.parse(localStorage.getItem('_ht_user_session'));
      } catch(e) {}

      if (session && session.email) {
        const email = session.email;
        const name = session.name || email.split('@')[0];
        const defaultStore = session.storeName || (name + " Studio");

        // Load seller data
        const sellerKey = '_ht_seller_data_' + email;
        let sellerData = null;
        try {
          sellerData = JSON.parse(localStorage.getItem(sellerKey));
        } catch(e) {}

        if (!sellerData) {
          sellerData = {
            storeName: defaultStore,
            email: email,
            iban: null,
            revenue: 0,
            balance: 0,
            salesCount: 0,
            rating: "Nouveau Vendeur",
            products: [],
            sales: []
          };
          localStorage.setItem(sellerKey, JSON.stringify(sellerData));
        }

        // Hydrate Header Card
        const studioEl = document.getElementById('seller-studio-name');
        const emailEl = document.getElementById('seller-email-display');
        const avatarEl = document.getElementById('seller-avatar-img');
        const ibanEl = document.getElementById('seller-iban-status');
        const topPayoutBtn = document.getElementById('btn-request-payout-top');

        if (studioEl) studioEl.textContent = sellerData.storeName;
        if (emailEl) emailEl.textContent = sellerData.email;
        if (avatarEl) avatarEl.src = `https://api.dicebear.com/7.x/identicon/svg?seed=${encodeURIComponent(sellerData.storeName || email)}`;

        if (ibanEl) {
          if (sellerData.iban) {
            ibanEl.textContent = `IBAN SEPA •••• ${sellerData.iban.slice(-4)} Vérifié`;
            ibanEl.className = "text-emerald-400 font-mono font-bold";
          } else {
            ibanEl.textContent = "Compte Bancaire Non Configuré";
            ibanEl.className = "text-amber-400 font-mono font-bold";
          }
        }

        if (topPayoutBtn) {
          topPayoutBtn.textContent = `💸 Demander Versement ($${sellerData.balance.toFixed(2)})`;
          if (sellerData.balance < 50) {
            topPayoutBtn.classList.add('opacity-75');
            topPayoutBtn.title = "Seuil minimal de versement : 50$";
          }
        }

        // Hydrate KPIs
        const kpiRev = document.getElementById('kpi-seller-revenue');
        const kpiBal = document.getElementById('kpi-seller-balance');
        const kpiSales = document.getElementById('kpi-seller-sales');
        const kpiRating = document.getElementById('kpi-seller-rating');

        if (kpiRev) kpiRev.textContent = `$${sellerData.revenue.toFixed(2)}`;
        if (kpiBal) kpiBal.textContent = `$${sellerData.balance.toFixed(2)}`;
        if (kpiSales) kpiSales.textContent = sellerData.salesCount;
        if (kpiRating) kpiRating.textContent = typeof sellerData.rating === 'number' ? `★ ${sellerData.rating.toFixed(2)}` : sellerData.rating;

        // Hydrate Products Badge & List
        const prodBadge = document.getElementById('badge-seller-prod-count');
        if (prodBadge) prodBadge.textContent = sellerData.products.length;

        const prodTbody = document.getElementById('seller-products-tbody');
        if (prodTbody) {
          if (sellerData.products.length === 0) {
            prodTbody.innerHTML = `
              <tr>
                <td colspan="7" class="py-12 text-center text-slate-400 font-mono text-xs">
                  <span class="text-3xl block mb-2">⚡</span>
                  <div class="text-white font-bold text-sm mb-1">Vous n'avez pas encore publié de template</div>
                  <p class="text-slate-500 max-w-md mx-auto mb-4">
                    Déposez votre premier workflow n8n, Make ou Supabase en 7 étapes. Notre scanner Sentinel AST vérifie la conformité en temps réel.
                  </p>
                  <button onclick="switchSellerTab('wizard')" class="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold font-mono text-xs transition-all shadow-glow-emerald">
                    + Déposer mon Premier Template ➔
                  </button>
                </td>
              </tr>
            `;
          } else {
            prodTbody.innerHTML = sellerData.products.map(p => `
              <tr class="hover:bg-slate-900/40 transition-colors">
                <td class="py-4 px-4">
                  <div class="font-bold text-white text-sm">${p.title}</div>
                  <div class="text-[11px] text-slate-400">${(p.ecosystem || 'FLOW').toUpperCase()} • ${p.category || 'Automation'}</div>
                </td>
                <td class="py-4 px-4 font-bold text-white">
                  ${p.isFree ? '<span class="text-emerald-400">GRATUIT</span>' : '$' + p.price}
                </td>
                <td class="py-4 px-4">
                  <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                    PUBLIÉ
                  </span>
                </td>
                <td class="py-4 px-4 text-cyan-400">v${p.version || '1.0.0'}</td>
                <td class="py-4 px-4 font-bold text-white">${p.salesCount || 0}</td>
                <td class="py-4 px-4 font-bold text-emerald-400">
                  $${((p.price || 0) * (p.salesCount || 0) * 0.8).toFixed(2)}
                </td>
                <td class="py-4 px-4 text-right space-x-2">
                  <a href="/templates/${p.slug}/" class="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700">
                    Voir
                  </a>
                  <button class="btn-new-version px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30" data-slug="${p.slug}">
                    + Version
                  </button>
                </td>
              </tr>
            `).join('');
          }
        }

        // Hydrate Recent Sales
        const salesTbody = document.getElementById('seller-recent-sales-tbody');
        if (salesTbody) {
          if (sellerData.sales.length === 0) {
            salesTbody.innerHTML = `
              <tr>
                <td colspan="6" class="py-10 text-center text-slate-500 font-mono text-xs">
                  Aucune vente enregistrée pour le moment.<br>
                  <span class="text-slate-600">Dès qu'un client achète votre blueprint sur la marketplace, vos 80% nets apparaîtront ici instantanément.</span>
                </td>
              </tr>
            `;
          } else {
            salesTbody.innerHTML = sellerData.sales.map(s => `
              <tr class="hover:bg-slate-900/40 transition-colors">
                <td class="py-3 px-4 text-white font-bold">${s.productTitle}</td>
                <td class="py-3 px-4 text-slate-400">${s.buyerEmail}</td>
                <td class="py-3 px-4 font-mono text-slate-300">$${Number(s.grossPrice).toFixed(2)}</td>
                <td class="py-3 px-4 font-mono text-rose-400">-$${Number(s.fee).toFixed(2)}</td>
                <td class="py-3 px-4 font-mono text-emerald-400 font-bold">+$${Number(s.net).toFixed(2)}</td>
                <td class="py-3 px-4 text-right"><span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px]">REVERSÉ</span></td>
              </tr>
            `).join('');
          }
        }

        // Hydrate SVG Chart: if 0 sales, show clean empty state
        const chartCont = document.getElementById('seller-chart-container');
        if (chartCont && sellerData.sales.length === 0) {
          chartCont.innerHTML = `
            <div class="h-44 flex flex-col items-center justify-center text-center p-6 bg-slate-950/40 rounded-2xl border border-slate-800/60">
              <span class="text-2xl mb-1 text-slate-600">📊</span>
              <span class="text-xs font-mono text-slate-400 font-bold">Aucune transaction cette semaine</span>
              <span class="text-[11px] text-slate-500 mt-0.5">Le graphique de vos revenus hebdomadaires s'actualisera automatiquement dès votre première vente.</span>
            </div>
          `;
        }

        // Hydrate Payout Settings Box
        const payoutBox = document.getElementById('seller-payout-status-box');
        if (payoutBox) {
          if (sellerData.iban) {
            payoutBox.innerHTML = `
              <div>
                <h3 class="text-sm font-bold text-white">Compte de Virement SEPA Connecté</h3>
                <p class="text-xs font-mono text-slate-400 mt-0.5">IBAN : ${sellerData.iban} (${sellerData.storeName})</p>
              </div>
              <button id="btn-request-payout-modal" class="px-5 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 text-slate-950 font-mono text-xs font-bold uppercase tracking-wider transition-all shadow-glow-emerald">
                Initier le Virement ($${sellerData.balance.toFixed(2)}) ➔
              </button>
            `;
          } else {
            payoutBox.innerHTML = `
              <div>
                <h3 class="text-sm font-bold text-amber-300">Compte bancaire non configuré</h3>
                <p class="text-xs font-mono text-slate-400 mt-0.5">Renseignez votre IBAN pour recevoir vos reversements nets de 80%.</p>
              </div>
              <button id="btn-configure-iban" class="px-5 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-mono text-xs font-bold uppercase tracking-wider transition-all">
                Configurer mon IBAN / Stripe ➔
              </button>
            `;
            document.getElementById('btn-configure-iban')?.addEventListener('click', () => {
              const newIban = prompt("Veuillez saisir votre IBAN pour recevoir vos versements (ex: FR76 1234 5678 9012 3456 7890 123):");
              if (newIban && newIban.trim().length >= 10) {
                sellerData.iban = newIban.trim().toUpperCase();
                localStorage.setItem(sellerKey, JSON.stringify(sellerData));
                alert("✓ Votre compte bancaire a été enregistré avec succès !");
                initSellerStudio();
              }
            });
          }
        }
      }
    }

    initSellerStudio();

    // Seller Logout
    document.getElementById('btn-seller-logout')?.addEventListener('click', async () => {
      try {
        await fetch('/api/marketplace/auth/logout', { method: 'POST' });
      } catch(e) {}
      localStorage.removeItem('_ht_user_session');
      alert("Vous avez été déconnecté avec succès.");
      window.location.href = '/login/';
    });
"""

if "initSellerStudio()" not in content:
    content = content.replace(
        "document.getElementById('create-coupon-form')?.addEventListener('submit', async (e) => {",
        seller_script_injection + "\n    document.getElementById('create-coupon-form')?.addEventListener('submit', async (e) => {"
    )

with open('site/src/pages/seller/index.astro', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] seller/index.astro updated with dynamic seller hydration.")
