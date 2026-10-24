import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

svg_path = Path('site/public/badges/winner-2026-supabase.svg')
png_path = Path('site/public/badges/winner-2026-supabase.png')

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width': 320, 'height': 120})
    svg_content = svg_path.read_text(encoding='utf-8')
    page.set_content('<!DOCTYPE html><html><body style="margin:0;background:transparent;">' + svg_content + '</body></html>')
    page.screenshot(path=str(png_path), type='png')
    browser.close()

print('Playwright rendered winner-2026-supabase.png successfully! Size:', png_path.stat().st_size)
