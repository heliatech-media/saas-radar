import os
import sys
import re
import json
from pathlib import Path

# Ensure UTF-8 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

root = Path('.')
site_dir = root / 'site'
blog_dir = site_dir / 'src' / 'content' / 'blog'
reviews_dir = site_dir / 'src' / 'content' / 'reviews'
public_dir = site_dir / 'public'
redirects_file = public_dir / '_redirects'

print("=" * 60)
print("🔍 HELIATECH FULL PLATFORM QUALITY & AUDIT SUITE")
print("=" * 60)

# 1. Audit Blog Images
blog_files = list(blog_dir.glob('*.md'))
print(f"\n[1/4] AUDITING BLOG ARTICLES & IMAGES ({len(blog_files)} files)")

missing_images = []
valid_images = []
empty_images = []
svg_fallbacks = []

for b in sorted(blog_files):
    text = b.read_text(encoding='utf-8')
    match = re.search(r'^image:\s*["\']?([^"\'\r\n]+)["\']?', text, re.MULTILINE)
    if not match or not match.group(1).strip():
        empty_images.append(b.name)
        continue
    img_rel = match.group(1).strip()
    clean_rel = img_rel.lstrip('/')
    target = public_dir / clean_rel

    if not target.exists():
        # Check if png vs svg
        alt_ext = target.with_suffix('.svg') if target.suffix == '.png' else target.with_suffix('.png')
        if alt_ext.exists():
            svg_fallbacks.append((b.name, img_rel, str(alt_ext.relative_to(public_dir))))
        else:
            missing_images.append((b.name, img_rel))
    else:
        valid_images.append((b.name, img_rel, target.stat().st_size))

print(f"  ✅ Valid image files on disk: {len(valid_images)}")
print(f"  ❌ Missing images (404): {len(missing_images)}")
for m in missing_images:
    print(f"     • {m[0]} -> {m[1]}")
print(f"  🔄 Extension mismatches (PNG vs SVG): {len(svg_fallbacks)}")
for s in svg_fallbacks:
    print(f"     • {s[0]} -> declared '{s[1]}', disk has '{s[2]}'")
print(f"  ⚠️ Empty/No image field: {len(empty_images)}")
for e in empty_images:
    print(f"     • {e}")

# 2. Audit Reviews Frontmatter & Affiliate URLs
review_files = list(reviews_dir.glob('*.md'))
print(f"\n[2/4] AUDITING REVIEWS & AFFILIATE TARGETS ({len(review_files)} reviews)")

reviews_audit = []
unmonetized_reviews = []

for r in sorted(review_files):
    text = r.read_text(encoding='utf-8')
    name_m = re.search(r'^name:\s*["\']?([^"\']+)["\']?', text, re.MULTILINE)
    aff_m = re.search(r'^affiliate_url:\s*["\']?([^"\']+)["\']?', text, re.MULTILINE)
    web_m = re.search(r'^website_url:\s*["\']?([^"\']+)["\']?', text, re.MULTILINE)

    name = name_m.group(1).strip() if name_m else r.stem
    aff = aff_m.group(1).strip() if aff_m else ""
    web = web_m.group(1).strip() if web_m else ""

    is_monetized = bool(
        aff and aff != web and (
            "?" in aff or 
            "partner" in aff or 
            "affiliate" in aff or 
            "ref=" in aff or 
            "via=" in aff or 
            "try." in aff or 
            "fpr" in aff or
            ".grsm.io" in aff or
            ".pxf.io" in aff
        )
    )
    
    reviews_audit.append({
        "slug": r.stem,
        "name": name,
        "affiliate_url": aff,
        "is_monetized": is_monetized
    })

    if not is_monetized:
        unmonetized_reviews.append(r.stem)

monetized_count = sum(1 for r in reviews_audit if r["is_monetized"])
print(f"  ✅ Monetized reviews: {monetized_count} / {len(reviews_audit)} ({round(monetized_count/len(reviews_audit)*100)}%)")
print(f"  ⚠️ Plain website fallback reviews: {len(unmonetized_reviews)}")
for u in unmonetized_reviews:
    print(f"     • {u}")

# 3. Audit Outbound /go/* Edge Redirects
print(f"\n[3/4] AUDITING /go/* EDGE REDIRECTS IN _redirects")
redirect_rules = {}
if redirects_file.exists():
    for line in redirects_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line.startswith('/go/') and ' ' in line:
            parts = line.split()
            slug = parts[0].replace('/go/', '').strip('/')
            target = parts[1].strip()
            redirect_rules[slug] = target

print(f"  ✅ Total /go/ routes configured: {len(redirect_rules)}")

# Check if every review slug has a corresponding /go/ route
missing_redirects = []
for r in review_files:
    if r.stem not in redirect_rules:
        missing_redirects.append(r.stem)

print(f"  ⚠️ Reviews without /go/ route: {len(missing_redirects)}")
for mr in missing_redirects:
    print(f"     • /go/{mr} is missing!")

# Check internal links across blog and reviews
print(f"\n[4/4] AUDITING INTERNAL LINKS IN CONTENT BODY")
broken_internal = []
valid_review_slugs = set(r.stem for r in review_files)
valid_blog_slugs = set(b.stem for b in blog_files)

for f in blog_files + review_files:
    content = f.read_text(encoding='utf-8')
    links = re.findall(r'\[([^\]]+)\]\((/blog/[^)]+|/reviews/[^)]+|/go/[^)]+)\)', content)
    for text_anchor, link_url in links:
        if link_url.startswith('/blog/'):
            s = link_url.replace('/blog/', '').strip('/').split('#')[0]
            if s and s not in valid_blog_slugs:
                broken_internal.append((f.name, link_url))
        elif link_url.startswith('/reviews/'):
            s = link_url.replace('/reviews/', '').strip('/').split('#')[0]
            if s and s not in valid_review_slugs:
                broken_internal.append((f.name, link_url))
        elif link_url.startswith('/go/'):
            s = link_url.replace('/go/', '').strip('/').split('#')[0]
            if s and s not in redirect_rules:
                broken_internal.append((f.name, link_url))

print(f"  Broken internal links found: {len(broken_internal)}")
for b in broken_internal:
    print(f"     • In {b[0]}: broken link '{b[1]}'")

print("\n--- Audit Script Completed Successfully ---")
