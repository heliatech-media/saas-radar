#!/usr/bin/env python3
import os
import re
from urllib.parse import urlparse

def audit_images():
    print("=== 1. AUDITING IMAGES ===")
    img_pattern = re.compile(r'src=["\'](/images/[^"\']+)["\']|image:\s*["\']?(/images/[^\s"\']+)["\']?')
    referenced_images = set()

    for root, dirs, files in os.walk('site/src'):
        for f in files:
            if f.endswith(('.astro', '.md', '.json', '.ts')):
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                        for m in img_pattern.findall(content):
                            img = m[0] if m[0] else m[1]
                            if img:
                                img_clean = img.split('?')[0].split('#')[0]
                                referenced_images.add((img_clean, p))
                except Exception:
                    pass

    missing = []
    for img, origin_file in sorted(list(referenced_images)):
        rel = img.lstrip('/')
        pub_path = os.path.join('site/public', rel)
        dist_path = os.path.join('site/dist', rel)
        if not os.path.exists(pub_path) and not os.path.exists(dist_path):
            missing.append((img, origin_file))

    print(f"Total referenced images: {len(referenced_images)}")
    print(f"Missing image references: {len(missing)}")
    for img, origin in missing:
        print(f"  [MISSING IMAGE] {img} (in {origin})")
    return missing

def audit_titles():
    print("\n=== 2. AUDITING LONG TITLES (>60 chars) ===")
    title_pattern = re.compile(r'title:\s*["\']([^"\']+)["\']|title=["\']([^"\']+)["\']')
    long_titles = []

    for root, dirs, files in os.walk('site/src/content'):
        for f in files:
            if f.endswith('.md'):
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                        lines = fh.readlines()
                        for line in lines[:15]:
                            m = title_pattern.search(line)
                            if m:
                                t = m.group(1) or m.group(2)
                                if len(t) > 60:
                                    long_titles.append((len(t), t, p))
                                break
                except Exception:
                    pass

    print(f"Total long titles found: {len(long_titles)}")
    for length, t, p in sorted(long_titles, reverse=True)[:15]:
        print(f"  [{length} chars] {t} ({os.path.basename(p)})")
    return long_titles

def audit_schema_markup():
    print("\n=== 3. AUDITING SCHEMA MARKUP IN TEMPLATES ===")
    schema_pattern = re.compile(r'@context|schema\.org', re.IGNORECASE)
    astro_files_with_schema = []
    for root, dirs, files in os.walk('site/src/pages'):
        for f in files:
            if f.endswith('.astro'):
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                        c = fh.read()
                        if schema_pattern.search(c):
                            astro_files_with_schema.append(p)
                except Exception:
                    pass
    print(f"Astro pages with JSON-LD / schema: {len(astro_files_with_schema)}")
    for af in astro_files_with_schema:
        print(f"  {af}")

if __name__ == '__main__':
    audit_images()
    audit_titles()
    audit_schema_markup()


def audit_internal_links():
    print("\n=== 4. AUDITING INTERNAL LINKS ===")
    href_pattern = re.compile(r'href=["\'](/[^"\'#?]+)["\']')
    internal_links = set()

    for root, dirs, files in os.walk('site/src'):
        for f in files:
            if f.endswith(('.astro', '.md')):
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                        for m in href_pattern.findall(fh.read()):
                            if not m.startswith(('/go/', '/api/', '/images/', '/data/', '/fonts/')):
                                internal_links.add((m, p))
                except Exception:
                    pass

    missing_routes = []
    for link, origin_file in sorted(list(internal_links)):
        norm = link.strip('/')
        dist_file = os.path.join('site/dist', norm, 'index.html')
        dist_root = os.path.join('site/dist', norm + '.html')
        if norm == '':
            dist_file = 'site/dist/index.html'
        if not os.path.exists(dist_file) and not os.path.exists(dist_root):
            missing_routes.append((link, origin_file))

    print(f"Total internal links tested: {len(internal_links)}")
    print(f"Broken internal links count: {len(missing_routes)}")
    for mr, of in missing_routes:
        print(f"  [BROKEN LINK] {mr} (found in {of})")
    return missing_routes

if __name__ == '__main__':
    audit_internal_links()
