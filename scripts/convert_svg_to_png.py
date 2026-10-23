import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT_DIR / "site" / "public" / "images" / "blog"

def convert_all_svgs():
    svg_files = list(IMAGES_DIR.glob("*.svg"))
    print(f"Found {len(svg_files)} SVGs to rasterize to high-res PNG (1200x630)...")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)

        for svg in svg_files:
            png_name = svg.stem + ".png"
            png_path = IMAGES_DIR / png_name
            svg_content = svg.read_text(encoding="utf-8")
            
            html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  html, body {{
    margin: 0;
    padding: 0;
    width: 1200px;
    height: 630px;
    overflow: hidden;
    background: #030712;
  }}
  svg {{
    width: 1200px;
    height: 630px;
    display: block;
  }}
</style>
</head>
<body>
{svg_content}
</body>
</html>"""
            page.set_content(html)
            page.screenshot(path=str(png_path), type="png")
            print(f"✓ Converted: {svg.name} -> {png_name} ({round(png_path.stat().st_size / 1024, 1)} KB)")

        browser.close()

if __name__ == "__main__":
    convert_all_svgs()
