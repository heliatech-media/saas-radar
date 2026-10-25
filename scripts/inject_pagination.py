"""
Script to inject 20-per-page pagination into site/src/pages/index.astro
"""
from pathlib import Path

path = Path("site/src/pages/index.astro")
content = path.read_text(encoding="utf-8")

# 1. Update header telemetry
old_telemetry = """        <div class="text-xs font-mono text-slate-400 border-l border-slate-800 pl-4">
          SHOWING: <span id="tool-count" class="text-cyan-300 font-bold">{toolsData.length}</span> OF {toolsData.length}
        </div>"""

new_telemetry = """        <div class="text-xs font-mono text-slate-400 border-l border-slate-800 pl-4 whitespace-nowrap">
          SHOWING: <span id="tool-count" class="text-cyan-300 font-bold">1–20</span> OF <span id="tool-total">{toolsData.length}</span>
        </div>"""

# 2. Add pagination controls right after #tools-grid
old_grid_end = """      ))}
    </div>
  </section>"""

new_grid_end = """      ))}
    </div>

    <!-- Pagination Controls (20 Software per page) -->
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
    </div>
  </section>"""

# 3. Replace script with full pagination logic
old_script = """  <!-- Interactive Search / Filter Controller -->
  <script is:inline>
    const searchInput = document.getElementById('search-input');
    const filterButtons = document.querySelectorAll('#category-filters button');
    const cards = Array.from(document.querySelectorAll('.tool-card'));
    const countSpan = document.getElementById('tool-count');
    const emptyState = document.getElementById('empty-state');
    const resetBtn = document.getElementById('reset-filters');
    const toolsGrid = document.getElementById('tools-grid');
    const sortRatingBtn = document.getElementById('sort-rating');
    const sortNameBtn = document.getElementById('sort-name');

    let activeCategory = 'All Systems';

    function filterTools() {
      const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
      let visibleCount = 0;

      cards.forEach(card => {
        const name = card.dataset.name || '';
        const category = card.dataset.category || '';
        const macro = card.dataset.macro || '';
        const tagline = card.dataset.tagline || '';

        const matchesSearch = !query || name.includes(query) || tagline.includes(query) || category.toLowerCase().includes(query) || macro.toLowerCase().includes(query);
        const matchesCategory = activeCategory === 'All Systems' || macro === activeCategory || category === activeCategory;

        if (matchesSearch && matchesCategory) {
          card.style.display = 'flex';
          visibleCount++;
        } else {
          card.style.display = 'none';
        }
      });

      if (countSpan) countSpan.textContent = visibleCount.toString();
      if (emptyState) {
        emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
      }
    }

    if (searchInput) {
      searchInput.addEventListener('input', filterTools);
    }

    // Keyboard shortcut (Cmd+K / Ctrl+K)
    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (searchInput) searchInput.focus();
      }
    });

    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        filterButtons.forEach(b => {
          b.className = 'filter-btn px-4 py-2 rounded-full text-xs font-medium tracking-wide transition-all duration-300 bg-slate-900/60 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800';
        });
        btn.className = 'filter-btn px-4 py-2 rounded-full text-xs font-bold tracking-wide transition-all duration-300 bg-gradient-to-r from-cyan-500 to-fuchsia-500 text-slate-950 shadow-glow-cyan scale-105 active';
        activeCategory = btn.getAttribute('data-category') || 'All Systems';
        filterTools();
      });
    });

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        if (filterButtons.length > 0) {
          filterButtons[0].click();
        } else {
          filterTools();
        }
      });
    }

    // Sorting handlers
    if (sortRatingBtn && toolsGrid) {
      sortRatingBtn.addEventListener('click', () => {
        cards.sort((a, b) => parseFloat(b.dataset.rating || 0) - parseFloat(a.dataset.rating || 0));
        cards.forEach(card => toolsGrid.appendChild(card));
        sortRatingBtn.className = 'px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold transition-all';
        if (sortNameBtn) sortNameBtn.className = 'px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800 transition-all';
      });
    }

    if (sortNameBtn && toolsGrid) {
      sortNameBtn.addEventListener('click', () => {
        cards.sort((a, b) => (a.dataset.name || '').localeCompare(b.dataset.name || ''));
        cards.forEach(card => toolsGrid.appendChild(card));
        sortNameBtn.className = 'px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold transition-all';
        if (sortRatingBtn) sortRatingBtn.className = 'px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800 transition-all';
      });
    }
  </script>"""

new_script = """  <!-- Interactive Search / Filter / Pagination Controller (20 Per Page) -->
  <script is:inline>
    const searchInput = document.getElementById('search-input');
    const filterButtons = document.querySelectorAll('#category-filters button');
    const cards = Array.from(document.querySelectorAll('.tool-card'));
    const countSpan = document.getElementById('tool-count');
    const totalSpan = document.getElementById('tool-total');
    const emptyState = document.getElementById('empty-state');
    const resetBtn = document.getElementById('reset-filters');
    const toolsGrid = document.getElementById('tools-grid');
    const sortRatingBtn = document.getElementById('sort-rating');
    const sortNameBtn = document.getElementById('sort-name');

    const paginationWrapper = document.getElementById('pagination-controls');
    const pageNumbersContainer = document.getElementById('page-numbers-container');
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');
    const curDisplay = document.getElementById('current-page-display');
    const totalDisplay = document.getElementById('total-pages-display');

    const PAGE_SIZE = 20;
    let currentPage = 1;
    let activeCategory = 'All Systems';
    let currentFilteredCards = [...cards];

    function renderPagination(totalFiltered) {
      const totalPages = Math.ceil(totalFiltered / PAGE_SIZE) || 1;
      if (currentPage > totalPages) currentPage = 1;

      if (!paginationWrapper) return;

      if (totalFiltered <= PAGE_SIZE) {
        paginationWrapper.style.display = totalFiltered === 0 ? 'none' : 'flex';
      } else {
        paginationWrapper.style.display = 'flex';
      }

      if (curDisplay) curDisplay.textContent = currentPage.toString();
      if (totalDisplay) totalDisplay.textContent = totalPages.toString();

      if (prevBtn) {
        prevBtn.disabled = currentPage === 1;
      }
      if (nextBtn) {
        nextBtn.disabled = currentPage === totalPages;
      }

      if (pageNumbersContainer) {
        pageNumbersContainer.innerHTML = '';
        for (let p = 1; p <= totalPages; p++) {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.textContent = p.toString();
          btn.className = p === currentPage
            ? 'w-8 h-8 rounded-xl text-xs font-mono font-bold bg-cyan-500 text-slate-950 shadow-glow-cyan'
            : 'w-8 h-8 rounded-xl text-xs font-mono font-medium text-slate-400 hover:text-white bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors cursor-pointer';
          btn.addEventListener('click', () => {
            currentPage = p;
            applyDisplayAndPagination(true);
          });
          pageNumbersContainer.appendChild(btn);
        }
      }
    }

    function applyDisplayAndPagination(shouldScroll = false) {
      const totalFiltered = currentFilteredCards.length;
      const totalPages = Math.ceil(totalFiltered / PAGE_SIZE) || 1;
      if (currentPage > totalPages) currentPage = 1;

      const startIndex = (currentPage - 1) * PAGE_SIZE;
      const endIndex = Math.min(startIndex + PAGE_SIZE, totalFiltered);

      // Hide all cards first
      cards.forEach(card => card.style.display = 'none');

      // Show only cards for the active page
      for (let i = startIndex; i < endIndex; i++) {
        if (currentFilteredCards[i]) {
          currentFilteredCards[i].style.display = 'flex';
        }
      }

      // Update header telemetry counter
      if (countSpan) {
        if (totalFiltered === 0) {
          countSpan.textContent = '0';
        } else {
          countSpan.textContent = `${startIndex + 1}–${endIndex}`;
        }
      }
      if (totalSpan) {
        totalSpan.textContent = totalFiltered.toString();
      }

      if (emptyState) {
        emptyState.style.display = totalFiltered === 0 ? 'block' : 'none';
      }

      renderPagination(totalFiltered);

      if (shouldScroll) {
        const matrixSection = document.getElementById('categories');
        if (matrixSection) {
          matrixSection.scrollIntoView({ behavior: 'smooth' });
        }
      }
    }

    function filterTools() {
      const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
      currentFilteredCards = [];

      cards.forEach(card => {
        const name = card.dataset.name || '';
        const category = card.dataset.category || '';
        const macro = card.dataset.macro || '';
        const tagline = card.dataset.tagline || '';

        const matchesSearch = !query || name.includes(query) || tagline.includes(query) || category.toLowerCase().includes(query) || macro.toLowerCase().includes(query);
        const matchesCategory = activeCategory === 'All Systems' || macro === activeCategory || category === activeCategory;

        if (matchesSearch && matchesCategory) {
          currentFilteredCards.push(card);
        }
      });

      currentPage = 1;
      applyDisplayAndPagination(false);
    }

    if (searchInput) {
      searchInput.addEventListener('input', filterTools);
    }

    // Keyboard shortcut (Cmd+K / Ctrl+K)
    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (searchInput) searchInput.focus();
      }
    });

    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        filterButtons.forEach(b => {
          b.className = 'filter-btn px-4 py-2 rounded-full text-xs font-medium tracking-wide transition-all duration-300 bg-slate-900/60 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800';
        });
        btn.className = 'filter-btn px-4 py-2 rounded-full text-xs font-bold tracking-wide transition-all duration-300 bg-gradient-to-r from-cyan-500 to-fuchsia-500 text-slate-950 shadow-glow-cyan scale-105 active';
        activeCategory = btn.getAttribute('data-category') || 'All Systems';
        filterTools();
      });
    });

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        if (searchInput) searchInput.value = '';
        if (filterButtons.length > 0) {
          filterButtons[0].click();
        } else {
          filterTools();
        }
      });
    }

    // Prev / Next pagination click handlers
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
          currentPage--;
          applyDisplayAndPagination(true);
        }
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(currentFilteredCards.length / PAGE_SIZE) || 1;
        if (currentPage < totalPages) {
          currentPage++;
          applyDisplayAndPagination(true);
        }
      });
    }

    // Sorting handlers
    if (sortRatingBtn && toolsGrid) {
      sortRatingBtn.addEventListener('click', () => {
        cards.sort((a, b) => parseFloat(b.dataset.rating || 0) - parseFloat(a.dataset.rating || 0));
        cards.forEach(card => toolsGrid.appendChild(card));
        sortRatingBtn.className = 'px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold transition-all';
        if (sortNameBtn) sortNameBtn.className = 'px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800 transition-all';
        filterTools();
      });
    }

    if (sortNameBtn && toolsGrid) {
      sortNameBtn.addEventListener('click', () => {
        cards.sort((a, b) => (a.dataset.name || '').localeCompare(b.dataset.name || ''));
        cards.forEach(card => toolsGrid.appendChild(card));
        sortNameBtn.className = 'px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 font-bold transition-all';
        if (sortRatingBtn) sortRatingBtn.className = 'px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 border border-slate-800 transition-all';
        filterTools();
      });
    }

    // Initial pagination execution on page load
    filterTools();
  </script>"""

# Normalize CRLF
content_norm = content.replace("\r\n", "\n")
old_telemetry_norm = old_telemetry.replace("\r\n", "\n")
new_telemetry_norm = new_telemetry.replace("\r\n", "\n")
old_grid_end_norm = old_grid_end.replace("\r\n", "\n")
new_grid_end_norm = new_grid_end.replace("\r\n", "\n")
old_script_norm = old_script.replace("\r\n", "\n")
new_script_norm = new_script.replace("\r\n", "\n")

if old_telemetry_norm in content_norm:
    content_norm = content_norm.replace(old_telemetry_norm, new_telemetry_norm)
    print("[OK] Telemetry updated")
else:
    print("[WARN] Telemetry pattern not found")

if old_grid_end_norm in content_norm:
    content_norm = content_norm.replace(old_grid_end_norm, new_grid_end_norm)
    print("[OK] Grid end & pagination bar added")
else:
    print("[WARN] Grid end pattern not found")

if old_script_norm in content_norm:
    content_norm = content_norm.replace(old_script_norm, new_script_norm)
    print("[OK] Script updated with pagination logic")
else:
    print("[WARN] Script pattern not found")

path.write_text(content_norm, encoding="utf-8")
print("[OK] Pagination injection complete!")
