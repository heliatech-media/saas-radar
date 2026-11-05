import re

with open('site/src/layouts/Layout.astro', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace desktop account container
target_desktop = """          <!-- Marketplace User Account Nav Pill -->
          <div id="nav-user-account-container" class="hidden sm:flex items-center">
            <a 
              id="nav-user-login-btn"
              href="/dashboard/" 
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-mono font-bold transition-all"
            >
              <span>🔑</span>
              <span>Mon Espace</span>
            </a>
          </div>"""

replacement_desktop = """          <!-- Marketplace User Account Nav Pill -->
          <div id="nav-user-account-container" class="hidden sm:flex items-center gap-2">
            <a 
              id="nav-user-login-btn"
              href="/login/" 
              class="px-2.5 py-1 text-slate-400 hover:text-white text-xs font-mono font-medium transition-colors"
            >
              Connexion
            </a>
            <a 
              id="nav-user-register-btn"
              href="/register/" 
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/35 text-xs font-mono font-bold transition-all shadow-sm shadow-cyan-500/10"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
              <span>S'inscrire</span>
            </a>
          </div>"""

# Replace in mobile drawer
target_mobile = """        <a href="/dashboard/" class="px-3.5 py-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-white/[0.06] transition-colors flex items-center justify-between">
          <span>Mon Espace Client</span>
          <span class="text-[10px] font-mono text-cyan-400">Accès</span>
        </a>"""

replacement_mobile = """        <a href="/dashboard/" class="px-3.5 py-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-white/[0.06] transition-colors flex items-center justify-between">
          <span>Mon Espace Client</span>
          <span class="text-[10px] font-mono text-cyan-400">Accès</span>
        </a>
        <div class="pt-2 border-t border-slate-800/80 flex items-center gap-2">
          <a href="/login/" class="flex-1 text-center py-2 rounded-xl text-slate-300 hover:text-white bg-slate-900 border border-slate-800 text-xs font-mono">
            Connexion
          </a>
          <a href="/register/" class="flex-1 text-center py-2 rounded-xl text-white bg-cyan-500/20 border border-cyan-500/40 text-xs font-mono font-bold">
            ✦ S'inscrire
          </a>
        </div>"""

# Add sync script before closing script
target_script = "        // 2. Linear-Style Mouse-Follow Radial Spotlight"
replacement_script = """        // 0. Dynamic Navbar User State
        try {
          const sessionRaw = localStorage.getItem('_ht_user_session');
          if (sessionRaw) {
            const session = JSON.parse(sessionRaw);
            const container = document.getElementById('nav-user-account-container');
            if (container && session && session.name) {
              const targetUrl = session.role === 'SELLER' ? '/seller/' : (session.role === 'ADMIN' ? '/admin/marketplace/' : '/dashboard/');
              container.innerHTML = `
                <a href="${targetUrl}" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-mono font-bold transition-all shadow-sm">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>${session.name.slice(0, 14)}</span>
                </a>
              `;
            }
          }
        } catch (e) {}

        // 2. Linear-Style Mouse-Follow Radial Spotlight"""

# Normalize CRLF for robust matching
content_normalized = content.replace('\r\n', '\n')
target_desktop_norm = target_desktop.replace('\r\n', '\n')
target_mobile_norm = target_mobile.replace('\r\n', '\n')
target_script_norm = target_script.replace('\r\n', '\n')

assert target_desktop_norm in content_normalized, "Desktop target not found"
assert target_mobile_norm in content_normalized, "Mobile target not found"
assert target_script_norm in content_normalized, "Script target not found"

content_normalized = content_normalized.replace(target_desktop_norm, replacement_desktop.replace('\r\n', '\n'))
content_normalized = content_normalized.replace(target_mobile_norm, replacement_mobile.replace('\r\n', '\n'))
content_normalized = content_normalized.replace(target_script_norm, replacement_script.replace('\r\n', '\n'))

with open('site/src/layouts/Layout.astro', 'w', encoding='utf-8') as f:
    f.write(content_normalized.replace('\n', '\r\n'))

print("[OK] Layout.astro updated with register and login nav links.")
