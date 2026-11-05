import os
import re

# 1. UPDATE dashboard/index.astro
with open('site/src/pages/dashboard/index.astro', 'r', encoding='utf-8') as f:
    dash_content = f.read()

# Add ids to orders table body if missing
dash_content = re.sub(
    r'<tbody class="divide-y divide-slate-800/80 text-slate-300">',
    r'<tbody class="divide-y divide-slate-800/80 text-slate-300" id="orders-table-body">',
    dash_content,
    count=1
)

# Enhance dashboard client script
dash_script_injection = """
    // =========================================================================
    // DYNAMIC USER HYDRATION (Scoped to logged-in user)
    // =========================================================================
    function initBuyerDashboard() {
      let session = null;
      try {
        session = JSON.parse(localStorage.getItem('_ht_user_session'));
      } catch(e) {}

      if (session && session.email) {
        const name = session.name || session.email.split('@')[0];
        const email = session.email;
        const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'HF';

        const nameEl = document.getElementById('buyer-display-name');
        const emailEl = document.getElementById('buyer-display-email');
        const avatarEl = document.getElementById('buyer-avatar-initials');

        if (nameEl) nameEl.textContent = name;
        if (emailEl) emailEl.textContent = email;
        if (avatarEl) avatarEl.textContent = initials;

        // Retrieve user-scoped library
        const libKey = '_ht_buyer_library_' + email;
        let userLibrary = [];
        try {
          userLibrary = JSON.parse(localStorage.getItem(libKey) || '[]');
        } catch(e) {}

        const count = userLibrary.length;
        const spent = userLibrary.reduce((sum, item) => sum + (Number(item.price) || 0), 0);
        const downloads = userLibrary.reduce((sum, item) => sum + (Number(item.downloads) || 0), 0);
        const hours = count * 24;

        const countEl = document.getElementById('stat-overview-count');
        const spentEl = document.getElementById('stat-overview-spent');
        const downloadsEl = document.getElementById('stat-overview-downloads');
        const savingsEl = document.getElementById('stat-overview-savings');
        const badgeLib = document.getElementById('badge-lib-count');

        if (countEl) countEl.textContent = count;
        if (spentEl) spentEl.textContent = `$${spent.toFixed(2)}`;
        if (downloadsEl) downloadsEl.textContent = downloads;
        if (savingsEl) savingsEl.textContent = `~${hours} Heures`;
        if (badgeLib) badgeLib.textContent = count;

        // Hydrate Recent Blueprints Grid
        const recentGrid = document.getElementById('recent-blueprints-grid');
        if (recentGrid) {
          if (count === 0) {
            recentGrid.innerHTML = `
              <div class="col-span-full p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center space-y-3">
                <span class="text-3xl block">📦</span>
                <h3 class="text-sm font-bold text-white">Votre bibliothèque est vide</h3>
                <p class="text-xs text-slate-400 max-w-md mx-auto">
                  Bonjour ${name} ! Vous n'avez pas encore acheté de blueprints. Parcourez notre catalogue certifié pour accélérer vos déploiements !
                </p>
                <div class="pt-2">
                  <a href="/templates/" class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono text-xs font-bold transition-all shadow-glow-cyan">
                    Découvrir le Catalogue ➔
                  </a>
                </div>
              </div>
            `;
          } else {
            recentGrid.innerHTML = userLibrary.slice(0, 4).map(item => `
              <div class="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between space-y-4">
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-bold uppercase">${item.ecosystem || 'FLOW'}</span>
                    <span class="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">Licence Active</span>
                  </div>
                  <h3 class="text-sm font-bold text-white mb-1">${item.title}</h3>
                  <p class="text-xs font-mono text-slate-400">Licence : ${item.licenseKey || 'HLT-LIC-' + Math.random().toString(36).slice(2, 8).toUpperCase()}</p>
                </div>
                <div class="flex items-center justify-between pt-3 border-t border-slate-800/80">
                  <span class="text-xs font-mono text-slate-500">v${item.version || '1.0.0'}</span>
                  <a href="/api/marketplace/buyer/download?slug=${item.slug}" download class="px-3.5 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-mono font-bold transition-all shadow-glow-cyan">
                    Télécharger .JSON ➔
                  </a>
                </div>
              </div>
            `).join('');
          }
        }

        // Hydrate Library Table
        const libTbody = document.getElementById('library-table-body');
        if (libTbody) {
          if (count === 0) {
            libTbody.innerHTML = `
              <tr>
                <td colspan="5" class="py-12 text-center text-slate-500 font-mono text-xs">
                  Aucun blueprint sous licence pour le compte <strong class="text-slate-300">${email}</strong>.
                  <div class="mt-3">
                    <a href="/templates/" class="text-cyan-400 underline font-bold hover:text-cyan-300">
                      Explorer la Marketplace et acquérir un premier template ➔
                    </a>
                  </div>
                </td>
              </tr>
            `;
          } else {
            libTbody.innerHTML = userLibrary.map(item => `
              <tr class="hover:bg-slate-900/40 transition-colors">
                <td class="py-4 px-4">
                  <div class="font-bold text-white text-sm">${item.title}</div>
                  <div class="text-[11px] text-slate-400">Acheté le ${item.purchaseDate || new Date().toLocaleDateString('fr-FR')}</div>
                </td>
                <td class="py-4 px-4">
                  <span class="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-[10px] font-bold uppercase">${item.ecosystem || 'FLOW'}</span>
                </td>
                <td class="py-4 px-4">
                  <span class="text-slate-300">v${item.version || '1.0.0'}</span>
                </td>
                <td class="py-4 px-4 font-mono text-cyan-400 text-[11px]">
                  ${item.licenseKey || 'HLT-LIC-' + Math.random().toString(36).slice(2, 8).toUpperCase()}
                </td>
                <td class="py-4 px-4 text-right">
                  <a href="/api/marketplace/buyer/download?slug=${item.slug}" download class="px-3.5 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs inline-block shadow-glow-cyan">
                    Télécharger ➔
                  </a>
                </td>
              </tr>
            `).join('');
          }
        }

        // Hydrate Orders Table
        const ordersTbody = document.getElementById('orders-table-body');
        if (ordersTbody) {
          if (count === 0) {
            ordersTbody.innerHTML = `
              <tr>
                <td colspan="6" class="py-12 text-center text-slate-500 font-mono text-xs">
                  Aucune commande enregistrée pour ce profil.
                </td>
              </tr>
            `;
          } else {
            ordersTbody.innerHTML = userLibrary.map((item, idx) => `
              <tr class="hover:bg-slate-900/40 transition-colors">
                <td class="py-4 px-4 font-bold text-cyan-400">#ORD-2026-${1000 + idx}</td>
                <td class="py-4 px-4 text-slate-400">${item.purchaseDate || new Date().toLocaleDateString('fr-FR')}</td>
                <td class="py-4 px-4 font-bold text-white">${item.title}</td>
                <td class="py-4 px-4 font-black text-emerald-400">$${item.price || 0}.00 USD</td>
                <td class="py-4 px-4">
                  <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">Payé</span>
                </td>
                <td class="py-4 px-4 text-right">
                  <button 
                    class="btn-open-invoice px-3 py-1 rounded bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 text-xs font-mono"
                    data-order-id="#ORD-2026-${1000 + idx}"
                    data-date="${item.purchaseDate || new Date().toLocaleDateString('fr-FR')}"
                    data-title="${item.title}"
                    data-amount="${item.price || 0}"
                  >
                    PDF Facture 📄
                  </button>
                </td>
              </tr>
            `).join('');
          }
        }
      }
    }

    initBuyerDashboard();
"""

if "initBuyerDashboard()" not in dash_content:
    dash_content = dash_content.replace(
        "document.getElementById('btn-buyer-logout')?.addEventListener('click', async () => {",
        dash_script_injection + "\n    document.getElementById('btn-buyer-logout')?.addEventListener('click', async () => {"
    )

with open('site/src/pages/dashboard/index.astro', 'w', encoding='utf-8') as f:
    f.write(dash_content)

print("[OK] dashboard/index.astro updated with dynamic user hydration.")
