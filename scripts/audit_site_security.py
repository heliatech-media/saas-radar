import os
import re
from urllib.parse import urlparse

def main():
    urls = set()
    url_pattern = re.compile(r'https?://[^\s\)\]\"\'<>]+')
    
    # 1. Check all content in site/src
    for root, dirs, files in os.walk('site/src'):
        for f in files:
            if f.endswith(('.md', '.astro', '.json', '.ts', '.js')):
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                        for m in url_pattern.findall(content):
                            # clean trailing punctuation
                            clean = m.rstrip('.,;:')
                            urls.add(clean)
                except Exception:
                    pass

    # 2. Check site/public/_redirects
    if os.path.exists('site/public/_redirects'):
        with open('site/public/_redirects', 'r', encoding='utf-8', errors='ignore') as fh:
            for line in fh:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[1].startswith('http'):
                    urls.add(parts[1])

    # 3. Check domain categorization
    domains = {}
    for u in urls:
        try:
            parsed = urlparse(u)
            dom = parsed.netloc.lower()
            if dom:
                domains.setdefault(dom, []).append(u)
        except Exception:
            pass

    # Flag list of known malicious / suspicious patterns or TLDs
    suspicious_tlds = ['.xyz', '.top', '.click', '.loan', '.work', '.gq', '.cf', '.tk', '.ml', '.buzz', '.rest']
    known_clean_services = [
        'heliatech.online', 'google.com', 'schema.org', 'cloudflare.com', 'github.com', 
        'jsdelivr.net', 'unpkg.com', 'tailwindcss.com', 'astro.build', 'resend.com', 
        'impact.com', 'hbagency.it', 'cloudfront.net', 'prebid.org', 'w3.org'
    ]

    suspicious = []
    for dom in domains:
        # Check if suspicious TLD
        if any(dom.endswith(tld) for tld in suspicious_tlds):
            suspicious.append((dom, 'suspicious_tld', domains[dom][:2]))
        # Check if IP address instead of domain
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', dom):
            suspicious.append((dom, 'raw_ip_address', domains[dom][:2]))

    print(f"TOTAL_UNIQUE_OUTBOUND_DOMAINS: {len(domains)}")
    print(f"SUSPICIOUS_DOMAINS_FOUND: {len(suspicious)}")
    if suspicious:
        for s in suspicious:
            print("SUSPICIOUS:", s)
    else:
        print("ALL_OUTBOUND_DOMAINS_CLEAN: TRUE")

if __name__ == '__main__':
    main()
