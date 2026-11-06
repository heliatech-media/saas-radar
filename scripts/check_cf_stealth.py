import time
import urllib.request

print("Starting to monitor Cloudflare Pages deployment...")
for i in range(20):
    time.sleep(10)
    try:
        req = urllib.request.Request('https://heliatech.online/templates/', headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        has_guard = 'Strict Production Stealth Access Gate' in html
        has_hidden = 'ht-nav-templates-link' in html
        print(f"Check {i+1} (at { (i+1)*10 }s): Guard deployed: {has_guard} | Nav hidden: {has_hidden}")
        if has_guard:
            print(">>> CLOUDFLARE PAGES HAS DEPLOYED THE STEALTH GUARD! <<<")
            break
    except Exception as e:
        print(f"Check {i+1}: {e}")
