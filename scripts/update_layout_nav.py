# -*- coding: utf-8 -*-
with open('site/src/layouts/Layout.astro', 'r', encoding='utf-8') as f:
    text = f.read()

# Normalize to LF for matching
is_crlf = '\r\n' in text
work_text = text.replace('\r\n', '\n')

target = """          <a href="/deals" class="group relative px-3.5 py-1.5 rounded-full text-slate-300 hover:text-white hover:bg-white/[0.05] transition-all duration-150 flex items-center gap-1.5">
            <span>Deals</span>
            <span class="inline-flex items-center px-1.5 py-0.2 rounded-full text-[9px] font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Perks
            </span>
          </a>"""

replacement = target + """\n          <a href="/templates" class="group relative px-3.5 py-1.5 rounded-full text-slate-300 hover:text-white hover:bg-white/[0.05] transition-all duration-150 flex items-center gap-1.5">
            <span>Templates</span>
            <span class="inline-flex items-center px-1.5 py-0.2 rounded-full text-[9px] font-mono font-bold bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
              Store
            </span>
          </a>"""

if target in work_text:
    work_text = work_text.replace(target, replacement, 1)
    print("Navbar link successfully added!")
else:
    print("Warning: Navbar target not found")

mobile_target = """        <a href="/deals" class="px-3.5 py-2.5 rounded-xl text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 transition-colors flex items-center justify-between">
          <span>Exclusive Perks & Deals</span>
          <span class="text-[10px] font-mono bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-500/30">Active</span>
        </a>"""

mobile_replacement = mobile_target + """\n        <a href="/templates" class="px-3.5 py-2.5 rounded-xl text-cyan-300 hover:text-cyan-200 hover:bg-cyan-500/10 transition-colors flex items-center justify-between">
          <span>Templates &amp; Blueprints</span>
          <span class="text-[10px] font-mono bg-cyan-500/20 px-2 py-0.5 rounded-full border border-cyan-500/30">Store</span>
        </a>\n        <a href="/portal" class="px-3.5 py-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-white/[0.06] transition-colors flex items-center justify-between">
          <span>Mon Espace Client</span>
          <span class="text-[10px] font-mono text-cyan-400">Accès</span>
        </a>"""

if mobile_target in work_text:
    work_text = work_text.replace(mobile_target, mobile_replacement, 1)
    print("Mobile nav links successfully added!")
else:
    print("Warning: Mobile target not found")

# Add Marketplace User Pill to right nav controls
right_target = """          <!-- Mobile Menu Toggle Button -->
          <button"""

right_replacement = """          <!-- Marketplace User Account Nav Pill -->
          <div id="nav-user-account-container" class="hidden sm:flex items-center">
            <a 
              id="nav-user-login-btn"
              href="/portal" 
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-mono font-bold transition-all"
            >
              <span>🔑</span>
              <span>Mon Espace</span>
            </a>
          </div>

          <!-- Mobile Menu Toggle Button -->
          <button"""

if right_target in work_text:
    work_text = work_text.replace(right_target, right_replacement, 1)
    print("Right nav account pill added!")

if is_crlf:
    work_text = work_text.replace('\n', '\r\n')

with open('site/src/layouts/Layout.astro', 'w', encoding='utf-8') as f:
    f.write(work_text)
print("Layout.astro saved!")
