import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

social_dir = Path('site/public/images/social')
social_dir.mkdir(parents=True, exist_ok=True)

avatar_png = social_dir / 'reddit-avatar.png'
banner_png = social_dir / 'reddit-banner.png'

# 1. Generate Reddit Avatar (512x512)
avatar_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#030712"/>
      <stop offset="50%" stop-color="#0b1329"/>
      <stop offset="100%" stop-color="#020617"/>
    </linearGradient>
    <linearGradient id="glow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06b6d4"/>
      <stop offset="100%" stop-color="#10b981"/>
    </linearGradient>
    <filter id="neon" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="12" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <rect width="512" height="512" rx="128" fill="url(#bg)"/>
  <rect x="8" y="8" width="496" height="496" rx="120" fill="none" stroke="url(#glow)" stroke-width="6" opacity="0.4"/>

  <!-- Core Shield -->
  <g transform="translate(256, 230)" filter="url(#neon)">
    <polygon points="0,-120 100,-40 100,70 0,130 -100,70 -100,-40" fill="#030712" stroke="url(#glow)" stroke-width="8"/>
    <!-- Cyber Core Star -->
    <text x="0" y="24" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="64" font-weight="900" fill="#06b6d4" text-anchor="middle">★</text>
  </g>

  <!-- Typography -->
  <text x="256" y="420" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="34" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="4">HELIATECH</text>
  <text x="256" y="455" font-family="'JetBrains Mono', monospace" font-size="16" font-weight="700" fill="#10b981" text-anchor="middle" letter-spacing="3">INDEPENDENT RADAR</text>
</svg>"""

# 2. Generate Reddit Banner (1200x400)
banner_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400" width="1200" height="400">
  <defs>
    <linearGradient id="bg-banner" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#020617"/>
      <stop offset="50%" stop-color="#0a1024"/>
      <stop offset="100%" stop-color="#030712"/>
    </linearGradient>
    <linearGradient id="text-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#22d3ee"/>
      <stop offset="50%" stop-color="#34d399"/>
      <stop offset="100%" stop-color="#f472b6"/>
    </linearGradient>
  </defs>

  <rect width="1200" height="400" fill="url(#bg-banner)"/>
  
  <!-- Subtle Grid Lines -->
  <g stroke="#1e293b" stroke-width="1" opacity="0.4">
    <line x1="0" y1="100" x2="1200" y2="100"/>
    <line x1="0" y1="200" x2="1200" y2="200"/>
    <line x1="0" y1="300" x2="1200" y2="300"/>
    <line x1="300" y1="0" x2="300" y2="400"/>
    <line x1="600" y1="0" x2="600" y2="400"/>
    <line x1="900" y1="0" x2="900" y2="400"/>
  </g>

  <!-- Left Accent Trophy -->
  <g transform="translate(140, 200)">
    <circle cx="0" cy="0" r="70" fill="#06b6d4" fill-opacity="0.1" stroke="#06b6d4" stroke-width="3"/>
    <text x="0" y="24" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="70" font-weight="900" fill="#22d3ee" text-anchor="middle">🛡️</text>
  </g>

  <!-- Content Hierarchy -->
  <text x="250" y="140" font-family="'JetBrains Mono', monospace" font-size="14" font-weight="700" fill="#06b6d4" letter-spacing="4">HELIATECH MEDIA • EMPIRICAL ACCREDITATION</text>
  <text x="250" y="210" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="52" font-weight="900" fill="#ffffff" letter-spacing="-1">The Gold Standard for Modern B2B SaaS</text>
  <text x="250" y="260" font-family="'Plus Jakarta Sans', system-ui, sans-serif" font-size="22" font-weight="600" fill="url(#text-grad)">Zero Sponsorship Bias • Cold Start Latency &amp; TCO Benchmarks</text>
  
  <!-- Pill Badges -->
  <rect x="250" y="295" width="220" height="34" rx="17" fill="#0f172a" stroke="#334155" stroke-width="1.5"/>
  <text x="360" y="317" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="#38bdf8" text-anchor="middle">🌐 heliatech.online</text>

  <rect x="490" y="295" width="260" height="34" rx="17" fill="#0f172a" stroke="#334155" stroke-width="1.5"/>
  <text x="620" y="317" font-family="'JetBrains Mono', monospace" font-size="12" font-weight="700" fill="#34d399" text-anchor="middle">⚡ 23 Autonomous AI Agents</text>
</svg>"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    
    # Avatar
    page = browser.new_page(viewport={'width': 512, 'height': 512})
    page.set_content('<!DOCTYPE html><html><body style="margin:0;background:transparent;">' + avatar_svg + '</body></html>')
    page.screenshot(path=str(avatar_png), type='png')
    page.close()
    print(f'Rendered Reddit Avatar: {avatar_png.name} ({avatar_png.stat().st_size} bytes)')

    # Banner
    page = browser.new_page(viewport={'width': 1200, 'height': 400})
    page.set_content('<!DOCTYPE html><html><body style="margin:0;background:transparent;">' + banner_svg + '</body></html>')
    page.screenshot(path=str(banner_png), type='png')
    page.close()
    print(f'Rendered Reddit Banner: {banner_png.name} ({banner_png.stat().st_size} bytes)')
    
    browser.close()

print('REDDIT BRANDING ASSETS GENERATED!')
