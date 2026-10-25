"""
Update Layout.astro with /calculator links
"""
from pathlib import Path

path = Path("site/src/layouts/Layout.astro")
content = path.read_text(encoding="utf-8")

# 1. Desktop Nav: Add Calculator right next to Deals
old_nav = """          <a href="/deals" class="group relative px-3.5 py-1.5 rounded-full text-slate-300 hover:text-white hover:bg-white/[0.05] transition-all duration-150 flex items-center gap-1.5">
            <span>Deals</span>
            <span class="inline-flex items-center px-1.5 py-0.2 rounded-full text-[9px] font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Perks
            </span>
          </a>"""

new_nav = """          <a href="/deals" class="group relative px-3.5 py-1.5 rounded-full text-slate-300 hover:text-white hover:bg-white/[0.05] transition-all duration-150 flex items-center gap-1.5">
            <span>Deals</span>
            <span class="inline-flex items-center px-1.5 py-0.2 rounded-full text-[9px] font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
              Perks
            </span>
          </a>
          <a href="/calculator" class="px-3.5 py-1.5 rounded-full text-slate-400 hover:text-white hover:bg-white/[0.05] transition-all duration-150">
            Calculator
          </a>"""

# Normalize CRLF
content_norm = content.replace("\r\n", "\n")
old_nav_norm = old_nav.replace("\r\n", "\n")
new_nav_norm = new_nav.replace("\r\n", "\n")

if old_nav_norm in content_norm:
    content_norm = content_norm.replace(old_nav_norm, new_nav_norm)
    print("[OK] Desktop nav updated")

# 2. Mobile Nav
old_mob = """        <a href="/deals" class="px-3.5 py-2.5 rounded-xl text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 transition-colors flex items-center justify-between">
          <span>Exclusive Perks & Deals</span>
          <span class="text-[10px] font-mono bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-500/30">Active</span>
        </a>"""

new_mob = """        <a href="/deals" class="px-3.5 py-2.5 rounded-xl text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 transition-colors flex items-center justify-between">
          <span>Exclusive Perks & Deals</span>
          <span class="text-[10px] font-mono bg-emerald-500/20 px-2 py-0.5 rounded-full border border-emerald-500/30">Active</span>
        </a>
        <a href="/calculator" class="px-3.5 py-2.5 rounded-xl text-slate-300 hover:text-white hover:bg-white/[0.06] transition-colors flex items-center justify-between">
          <span>TCO Calculator & Audit</span>
          <span class="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">Free</span>
        </a>"""

old_mob_norm = old_mob.replace("\r\n", "\n")
new_mob_norm = new_mob.replace("\r\n", "\n")

if old_mob_norm in content_norm:
    content_norm = content_norm.replace(old_mob_norm, new_mob_norm)
    print("[OK] Mobile nav updated")

# 3. Footer Link
old_foot = """            <a href="/deals" class="text-slate-400 hover:text-emerald-400 transition-colors">SaaS Deals & Perks</a>"""
new_foot = """            <a href="/deals" class="text-slate-400 hover:text-emerald-400 transition-colors">SaaS Deals & Perks</a>
            <span class="text-slate-700">•</span>
            <a href="/calculator" class="text-slate-400 hover:text-cyan-400 transition-colors">TCO Calculator</a>"""

old_foot_norm = old_foot.replace("\r\n", "\n")
new_foot_norm = new_foot.replace("\r\n", "\n")

if old_foot_norm in content_norm:
    content_norm = content_norm.replace(old_foot_norm, new_foot_norm)
    print("[OK] Footer links updated")

path.write_text(content_norm, encoding="utf-8")
