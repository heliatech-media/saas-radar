"""
Add /partner link to footer in Layout.astro
"""
from pathlib import Path

path = Path("site/src/layouts/Layout.astro")
content = path.read_text(encoding="utf-8")

old_str = '<a href="/media-kit" class="text-slate-400 hover:text-fuchsia-400 transition-colors">Media Kit</a>'
new_str = '<a href="/partner" class="text-cyan-400 hover:text-cyan-300 font-bold transition-colors">Submit SaaS / Partner</a>\n            <span class="text-slate-700">•</span>\n            ' + old_str

content_norm = content.replace("\r\n", "\n")
old_str_norm = old_str.replace("\r\n", "\n")

if old_str_norm in content_norm:
    content_norm = content_norm.replace(old_str_norm, new_str)
    path.write_text(content_norm, encoding="utf-8")
    print("[OK] Layout footer updated with /partner")
else:
    print("[INFO] Pattern not found")
