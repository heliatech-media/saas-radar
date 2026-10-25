"""
Script to inject ToolIcon into:
1. site/src/pages/index.astro
2. site/src/pages/deals/index.astro
3. site/src/pages/reviews/[slug].astro
"""

from pathlib import Path

# 1. Update site/src/pages/index.astro
index_path = Path("site/src/pages/index.astro")
index_content = index_path.read_text(encoding="utf-8")

if "ToolIcon" not in index_content:
    # Add import
    index_content = index_content.replace(
        "import Layout from '../layouts/Layout.astro';",
        "import Layout from '../layouts/Layout.astro';\nimport ToolIcon from '../components/ToolIcon.astro';"
    )
    
    # Replace Spotlight tool title
    old_spotlight = """            <h3 class="text-2xl font-black text-white mb-2 group-hover:text-cyan-300 transition-colors">
              {tool.name}
            </h3>"""
    new_spotlight = """            <div class="flex items-center gap-3 mb-3">
              <ToolIcon name={tool.name} slug={tool.slug} size="md" />
              <h3 class="text-2xl font-black text-white group-hover:text-cyan-300 transition-colors">
                {tool.name}
              </h3>
            </div>"""
    index_content = index_content.replace(old_spotlight, new_spotlight)

    # Replace Matrix grid tool title
    old_grid = """            <!-- Title & Tagline -->
            <h3 class="text-2xl font-black text-white mb-3 group-hover:text-cyan-300 transition-colors tracking-tight">
              {tool.name}
            </h3>"""
    new_grid = """            <!-- Title & Tagline -->
            <div class="flex items-center gap-3 mb-3">
              <ToolIcon name={tool.name} slug={tool.slug} size="md" />
              <h3 class="text-2xl font-black text-white group-hover:text-cyan-300 transition-colors tracking-tight">
                {tool.name}
              </h3>
            </div>"""
    index_content = index_content.replace(old_grid, new_grid)

    index_path.write_text(index_content, encoding="utf-8")
    print("[OK] Updated site/src/pages/index.astro with ToolIcon")
else:
    print("[INFO] site/src/pages/index.astro already contains ToolIcon")


# 2. Update site/src/pages/deals/index.astro
deals_path = Path("site/src/pages/deals/index.astro")
deals_content = deals_path.read_text(encoding="utf-8")

if "ToolIcon" not in deals_content:
    deals_content = deals_content.replace(
        "import Layout from '../../layouts/Layout.astro';",
        "import Layout from '../../layouts/Layout.astro';\nimport ToolIcon from '../../components/ToolIcon.astro';"
    )
    
    old_deal_title = """            <!-- Title & Tool -->
            <div class="flex items-baseline justify-between gap-2 mb-2">
              <h2 class="text-xl sm:text-2xl font-bold text-white group-hover:text-cyan-300 transition-colors">
                {deal.toolName}
              </h2>
              <span class="text-xs font-mono text-slate-500 uppercase tracking-wider">
                {deal.category}
              </span>
            </div>"""
    new_deal_title = """            <!-- Title & Tool with Brand Icon -->
            <div class="flex items-center justify-between gap-3 mb-3">
              <div class="flex items-center gap-3">
                <ToolIcon name={deal.toolName} slug={deal.toolSlug} size="md" />
                <h2 class="text-xl sm:text-2xl font-bold text-white group-hover:text-cyan-300 transition-colors">
                  {deal.toolName}
                </h2>
              </div>
              <span class="text-xs font-mono text-slate-500 uppercase tracking-wider hidden sm:inline-block">
                {deal.category}
              </span>
            </div>"""
    deals_content = deals_content.replace(old_deal_title, new_deal_title)

    deals_path.write_text(deals_content, encoding="utf-8")
    print("[OK] Updated site/src/pages/deals/index.astro with ToolIcon")
else:
    print("[INFO] site/src/pages/deals/index.astro already contains ToolIcon")


# 3. Update site/src/pages/reviews/[slug].astro
review_path = Path("site/src/pages/reviews/[slug].astro")
review_content = review_path.read_text(encoding="utf-8")

if "ToolIcon" not in review_content:
    review_content = review_content.replace(
        "import Layout from '../../layouts/Layout.astro';",
        "import Layout from '../../layouts/Layout.astro';\nimport ToolIcon from '../../components/ToolIcon.astro';"
    )

    old_hero_title = """        <div>
          <span class="inline-block px-3 py-1 rounded-full text-[11px] font-mono font-medium bg-slate-800 text-cyan-300 border border-slate-700 mb-3">
            {tool.category}
          </span>
          <h1 class="text-4xl sm:text-6xl font-black text-white tracking-tight">
            {tool.name}
          </h1>
        </div>"""
    new_hero_title = """        <div>
          <span class="inline-block px-3 py-1 rounded-full text-[11px] font-mono font-medium bg-slate-800 text-cyan-300 border border-slate-700 mb-4">
            {tool.category}
          </span>
          <div class="flex items-center gap-4 sm:gap-5">
            <ToolIcon name={tool.name} websiteUrl={tool.website_url} slug={slug} size="xl" />
            <h1 class="text-4xl sm:text-6xl font-black text-white tracking-tight">
              {tool.name}
            </h1>
          </div>
        </div>"""
    review_content = review_content.replace(old_hero_title, new_hero_title)

    review_path.write_text(review_content, encoding="utf-8")
    print("[OK] Updated site/src/pages/reviews/[slug].astro with ToolIcon")
else:
    print("[INFO] site/src/pages/reviews/[slug].astro already contains ToolIcon")
