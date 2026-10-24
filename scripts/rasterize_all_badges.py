import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

# Rasterize all badges in site/public/badges
badges_dir = Path('site/public/badges')
with sync_playwright() as p:
    browser = p.chromium.launch()
    for svg_file in badges_dir.glob('*.svg'):
        png_file = svg_file.with_suffix('.png')
        page = browser.new_page(viewport={'width': 320, 'height': 120})
        svg_content = svg_file.read_text(encoding='utf-8')
        page.set_content('<!DOCTYPE html><html><body style="margin:0;background:transparent;">' + svg_content + '</body></html>')
        page.screenshot(path=str(png_file), type='png')
        page.close()
        print(f'Rendered badge PNG: {png_file.name} ({png_file.stat().st_size} bytes)')
    
    # Also verify blog/supabase.svg
    blog_svg = Path('site/public/images/blog/supabase.svg')
    blog_png = Path('site/public/images/blog/supabase.png')
    page = browser.new_page(viewport={'width': 1200, 'height': 630})
    page.set_content('<!DOCTYPE html><html><body style="margin:0;background:#030712;">' + blog_svg.read_text(encoding='utf-8') + '</body></html>')
    page.screenshot(path=str(blog_png), type='png')
    page.close()
    print(f'Rendered blog PNG: {blog_png.name} ({blog_png.stat().st_size} bytes)')
    
    browser.close()

print('ALL BADGES AND BLOG ASSETS RASTERIZED SUCCESSFULLY!')
