"""
Remove duplicate misplaced pagination block above Active Software Matrix
"""
from pathlib import Path

path = Path("site/src/pages/index.astro")
content = path.read_text(encoding="utf-8")

# Pattern to remove (the one right before </section> of Spotlight)
misplaced_block = """    <!-- Pagination Controls (20 Software per page) -->
    <div id="pagination-controls" class="mt-12 flex flex-col sm:flex-row items-center justify-between gap-4 p-4 sm:p-5 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl">
      <div class="text-xs font-mono text-slate-400">
        Page <span id="current-page-display" class="text-white font-bold">1</span> sur <span id="total-pages-display" class="text-white font-bold">2</span>
        <span class="text-slate-600 mx-2">•</span>
        <span class="text-slate-400 font-medium">20 logiciels par page</span>
      </div>

      <div class="flex items-center gap-2">
        <button 
          id="prev-page-btn"
          type="button"
          class="px-4 py-2 rounded-xl text-xs font-mono font-medium transition-all duration-200 bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700 disabled:opacity-30 disabled:pointer-events-none flex items-center gap-1.5 cursor-pointer"
        >
          <span>←</span>
          <span>Précédent</span>
        </button>

        <div id="page-numbers-container" class="flex items-center gap-1.5">
          <!-- Dynamically populated page buttons -->
        </div>

        <button 
          id="next-page-btn"
          type="button"
          class="px-4 py-2 rounded-xl text-xs font-mono font-medium transition-all duration-200 bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700 disabled:opacity-30 disabled:pointer-events-none flex items-center gap-1.5 cursor-pointer"
        >
          <span>Suivant</span>
          <span>→</span>
        </button>
      </div>
    </div>"""

content_norm = content.replace("\r\n", "\n")
block_norm = misplaced_block.replace("\r\n", "\n")

# Find first occurrence (which is the misplaced one in Spotlight)
first_idx = content_norm.find(block_norm)
last_idx = content_norm.rfind(block_norm)

print("First occurrence at:", first_idx)
print("Last occurrence at:", last_idx)

if first_idx != -1 and first_idx != last_idx:
    # Remove only the first occurrence
    # Look for the preceding newline if any
    content_norm = content_norm[:first_idx].rstrip() + "\n" + content_norm[first_idx + len(block_norm):].lstrip("\n")
    path.write_text(content_norm, encoding="utf-8")
    print("[OK] Removed misplaced top pagination block! Bottom pagination remains intact.")
else:
    print("[WARN] Did not find two occurrences")
