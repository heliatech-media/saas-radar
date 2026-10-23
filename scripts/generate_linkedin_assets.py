"""
Generate high-DPI official LinkedIn Brand Assets for Helia Tech:
1. Banner (1584x396) - Luxury Cyber Dark, Titanium & Gold, Global Observatory Branding
2. Avatar / Profile (400x400) - Hexagonal Monogram Logo with Cyan/Gold Pulse
"""

import sys
from pathlib import Path
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from playwright.sync_api import sync_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
SOCIAL_DIR = ROOT_DIR / "site" / "public" / "images" / "social"
SOCIAL_DIR.mkdir(parents=True, exist_ok=True)

# 1. Official LinkedIn Banner SVG (1584 x 396)
BANNER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1584 396" width="1584" height="396">
  <defs>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="40%" stop-color="#030712"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="cyan-gold" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#06b6d4"/>
      <stop offset="50%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#fbbf24"/>
    </linearGradient>
    <linearGradient id="glow-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.05"/>
    </linearGradient>
    <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M 48 0 L 0 0 0 48" fill="none" stroke="#1e293b" stroke-width="0.8" stroke-opacity="0.4"/>
      <circle cx="0" cy="0" r="1.5" fill="#06b6d4" fill-opacity="0.4"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="1584" height="396" fill="url(#bg-grad)"/>
  <rect width="1584" height="396" fill="url(#grid)"/>

  <!-- Ambient Light Orbs -->
  <circle cx="1300" cy="80" r="280" fill="#06b6d4" fill-opacity="0.08" filter="blur(60px)"/>
  <circle cx="400" cy="350" r="220" fill="#f59e0b" fill-opacity="0.05" filter="blur(50px)"/>

  <!-- Left Accent Tech Pillars -->
  <path d="M 0 0 L 180 0 L 100 396 L 0 396 Z" fill="url(#glow-grad)"/>
  <line x1="180" y1="0" x2="100" y2="396" stroke="#06b6d4" stroke-width="2" stroke-opacity="0.6"/>

  <!-- Center-Right Editorial Focus -->
  <g transform="translate(360, 110)">
    <!-- Badge -->
    <rect x="0" y="0" width="310" height="32" rx="16" fill="#0f172a" stroke="#06b6d4" stroke-width="1.2" stroke-opacity="0.7"/>
    <circle cx="18" cy="16" r="4" fill="#06b6d4"/>
    <text x="32" y="21" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="12" font-weight="700" fill="#38bdf8" letter-spacing="2">
      AUTONOMOUS B2B OBSERVATORY
    </text>

    <!-- Main Title -->
    <text x="0" y="85" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="52" font-weight="900" fill="#ffffff" letter-spacing="-1">
      HELIA <tspan fill="url(#cyan-gold)">TECH</tspan>
    </text>

    <!-- Subtitle -->
    <text x="0" y="125" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="20" font-weight="500" fill="#94a3b8" letter-spacing="0.5">
      Software Teardowns • Enterprise Workflows • Empirical Benchmarks
    </text>

    <!-- Domain Pill -->
    <g transform="translate(0, 150)">
      <rect x="0" y="0" width="220" height="36" rx="8" fill="#1e293b" fill-opacity="0.7" stroke="#334155" stroke-width="1"/>
      <text x="18" y="23" font-family="'JetBrains Mono', monospace" font-size="14" font-weight="600" fill="#38bdf8">
        heliatech.online
      </text>
    </g>
  </g>

  <!-- Right Decorative Metrics Radar -->
  <g transform="translate(1220, 90)">
    <!-- Tech Frame -->
    <rect x="0" y="0" width="280" height="210" rx="16" fill="#090d16" fill-opacity="0.8" stroke="#1e293b" stroke-width="1.5"/>
    <rect x="0" y="0" width="280" height="3" fill="url(#cyan-gold)"/>
    
    <text x="24" y="38" font-family="'JetBrains Mono', monospace" font-size="11" font-weight="700" fill="#06b6d4" letter-spacing="1.5">
      LIVE TELEMETRY // MATRIX
    </text>
    
    <g transform="translate(24, 60)">
      <text x="0" y="18" font-family="'Plus Jakarta Sans', sans-serif" font-size="28" font-weight="800" fill="#ffffff">
        100,000+
      </text>
      <text x="0" y="36" font-family="'Plus Jakarta Sans', sans-serif" font-size="12" font-weight="500" fill="#64748b">
        Monthly Executive Readers
      </text>
    </g>

    <g transform="translate(24, 125)">
      <text x="0" y="18" font-family="'Plus Jakarta Sans', sans-serif" font-size="28" font-weight="800" fill="#fbbf24">
        100% Free
      </text>
      <text x="0" y="36" font-family="'Plus Jakarta Sans', sans-serif" font-size="12" font-weight="500" fill="#64748b">
        Unbiased Empirical Audits
      </text>
    </g>
  </g>
</svg>"""

# 2. Official LinkedIn Avatar / Profile SVG (400 x 400)
AVATAR_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs>
    <linearGradient id="av-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="50%" stop-color="#090d16"/>
      <stop offset="100%" stop-color="#030712"/>
    </linearGradient>
    <linearGradient id="cyan-glow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4"/>
      <stop offset="50%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#f59e0b"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="400" height="400" rx="80" fill="url(#av-bg)"/>
  
  <!-- Outer Tech Border -->
  <rect x="12" y="12" width="376" height="376" rx="72" fill="none" stroke="#1e293b" stroke-width="2"/>
  <circle cx="200" cy="200" r="140" fill="#06b6d4" fill-opacity="0.08" filter="blur(30px)"/>

  <!-- Hexagonal Tech Core -->
  <polygon points="200,80 290,132 290,268 200,320 110,268 110,132" 
           fill="#0f172a" stroke="url(#cyan-glow)" stroke-width="4"/>

  <!-- Modern Monogram H & T -->
  <path d="M 160 145 L 160 255 M 160 200 L 210 200 M 210 145 L 210 255" 
        stroke="#ffffff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>
  
  <circle cx="240" cy="155" r="8" fill="#fbbf24"/>
</svg>"""


def main():
    banner_svg_path = SOCIAL_DIR / "linkedin-banner.svg"
    banner_png_path = SOCIAL_DIR / "linkedin-banner.png"
    avatar_svg_path = SOCIAL_DIR / "linkedin-avatar.svg"
    avatar_png_path = SOCIAL_DIR / "linkedin-avatar.png"

    banner_svg_path.write_text(BANNER_SVG, encoding="utf-8")
    avatar_svg_path.write_text(AVATAR_SVG, encoding="utf-8")
    print(f"✅ Generated {banner_svg_path}")
    print(f"✅ Generated {avatar_svg_path}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        # 1. Rasterize Banner
        page1 = browser.new_page(viewport={"width": 1584, "height": 396}, device_scale_factor=1)
        page1.set_content(f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#020617;overflow:hidden;">{BANNER_SVG}</body></html>""")
        page1.screenshot(path=str(banner_png_path), type="png")
        print(f"✅ Rasterized {banner_png_path} ({banner_png_path.stat().st_size / 1024:.1f} KB)")
        page1.close()

        # 2. Rasterize Avatar
        page2 = browser.new_page(viewport={"width": 400, "height": 400}, device_scale_factor=1)
        page2.set_content(f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#020617;overflow:hidden;">{AVATAR_SVG}</body></html>""")
        page2.screenshot(path=str(avatar_png_path), type="png")
        print(f"✅ Rasterized {avatar_png_path} ({avatar_png_path.stat().st_size / 1024:.1f} KB)")
        page2.close()

        browser.close()


if __name__ == "__main__":
    main()
