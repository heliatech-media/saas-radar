"""
Complete injection script for ToolIcon across the Astro codebase.
"""
from pathlib import Path

# 1. Update site/src/pages/reviews/[slug].astro
rev_file = Path("site/src/pages/reviews/[slug].astro")
rev_content = rev_file.read_text(encoding="utf-8")

old_comp = """                <div class="flex items-center gap-2">
                  <span class="font-bold text-white text-base">{tool.name}</span>
                  <span class="text-xs font-mono text-slate-500 uppercase px-2 py-0.5 rounded bg-slate-800">VS</span>
                  <span class="font-bold text-slate-300 text-base">{item.competitor}</span>
                </div>"""

new_comp = """                <div class="flex items-center gap-2.5">
                  <ToolIcon name={tool.name} websiteUrl={tool.website_url} slug={slug} size="xs" />
                  <span class="font-bold text-white text-base">{tool.name}</span>
                  <span class="text-xs font-mono text-slate-500 uppercase px-2 py-0.5 rounded bg-slate-800">VS</span>
                  <ToolIcon name={item.competitor} size="xs" />
                  <span class="font-bold text-slate-300 text-base">{item.competitor}</span>
                </div>"""

# Normalize CRLF for replacement
normalized_rev = rev_content.replace("\r\n", "\n")
if old_comp in normalized_rev:
    normalized_rev = normalized_rev.replace(old_comp, new_comp)
    rev_file.write_text(normalized_rev, encoding="utf-8")
    print("[OK] Updated reviews/[slug].astro competitor matrix with ToolIcon")
else:
    print("[INFO] reviews/[slug].astro competitor matrix already updated or pattern not matched")

# Also check deploy button
old_deploy = """          <span>Deploy {tool.name} Free</span>
          <span>↗</span>"""
new_deploy = """          <ToolIcon name={tool.name} websiteUrl={tool.website_url} slug={slug} size="xs" />
          <span>Deploy {tool.name} Free</span>
          <span>↗</span>"""

if old_deploy in normalized_rev:
    normalized_rev = normalized_rev.replace(old_deploy, new_deploy)
    rev_file.write_text(normalized_rev, encoding="utf-8")
    print("[OK] Updated reviews/[slug].astro deploy button with ToolIcon")
else:
    print("[INFO] reviews/[slug].astro deploy button already has ToolIcon or pattern not matched")
