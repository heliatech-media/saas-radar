import os
import re
from pathlib import Path
from urllib.parse import urlparse

dist_dir = Path("site/dist")
print(f"Auditing compiled HTML pages in: {dist_dir.resolve()}")

html_files = list(dist_dir.rglob("*.html"))
print(f"Found {len(html_files)} compiled HTML files.")

broken_images = []
checked_images = set()
valid_local_count = 0
valid_external_count = 0

for hf in html_files:
    rel_html = hf.relative_to(dist_dir)
    content = hf.read_text(encoding="utf-8")
    
    # 1. Check all <img src="...">
    img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    for src in img_matches:
        # Strip query params like ?v=20261024b
        parsed = urlparse(src)
        clean_path = parsed.path
        
        if parsed.scheme in ["http", "https"]:
            valid_external_count += 1
            continue
            
        checked_images.add(clean_path)
        
        # Resolve path
        if clean_path.startswith("/"):
            target_file = dist_dir / clean_path.lstrip("/")
        else:
            target_file = hf.parent / clean_path
            
        if not target_file.exists():
            broken_images.append({
                "html_file": str(rel_html),
                "tag": "img",
                "src": src,
                "target_path": str(target_file)
            })
        else:
            valid_local_count += 1

    # 2. Check all <source srcset="...">
    source_matches = re.findall(r'<source[^>]+srcset=["\']([^"\']+)["\']', content)
    for srcset in source_matches:
        # srcset could have multiple comma separated entries or single
        entries = [e.strip().split()[0] for e in srcset.split(",") if e.strip()]
        for entry in entries:
            parsed = urlparse(entry)
            clean_path = parsed.path
            
            if parsed.scheme in ["http", "https"]:
                valid_external_count += 1
                continue
                
            checked_images.add(clean_path)
            
            if clean_path.startswith("/"):
                target_file = dist_dir / clean_path.lstrip("/")
            else:
                target_file = hf.parent / clean_path
                
            if not target_file.exists():
                broken_images.append({
                    "html_file": str(rel_html),
                    "tag": "source",
                    "src": entry,
                    "target_path": str(target_file)
                })
            else:
                valid_local_count += 1

print("\n--- DIST IMAGE INTEGRITY RESULTS ---")
print(f"Total HTML files inspected: {len(html_files)}")
print(f"Unique local image URLs checked: {len(checked_images)}")
print(f"Valid local image references: {valid_local_count}")
print(f"Valid external image references (e.g. Google Favicons): {valid_external_count}")
print(f"Broken image references: {len(broken_images)}")

if broken_images:
    print("\n[BROKEN IMAGES DETECTED]:")
    for b in broken_images[:20]:
        print(f"  ❌ In {b['html_file']}: <{b['tag']} src='{b['src']}'> -> File not found: {b['target_path']}")
    if len(broken_images) > 20:
        print(f"  ... and {len(broken_images) - 20} more.")
else:
    print("\n[SUCCESS] Zero broken images across the entire generated site!")
