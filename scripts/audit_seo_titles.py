import glob
import os
import re

files = glob.glob('site/src/content/blog/*.md')
print(f"Total blog files: {len(files)}")

patterns = {
    "evolution-guide": 0,
    "vs": 0,
    "best-alternatives": 0,
    "breaking": 0,
    "other": 0
}

for f in sorted(files):
    base = os.path.basename(f)
    if "evolution-guide" in base:
        patterns["evolution-guide"] += 1
    elif "-vs-" in base:
        patterns["vs"] += 1
    elif "best-" in base or "alternatives" in base:
        patterns["best-alternatives"] += 1
    elif "breaking" in base or "leak" in base:
        patterns["breaking"] += 1
    else:
        patterns["other"] += 1

print("Patterns count:", patterns)

print("\n--- SAMPLE TITLES ---")
for f in sorted(files)[:25]:
    content = open(f, encoding='utf-8', errors='ignore').read()
    m = re.search(r'^title:\s*[\'"]?([^\n\'"]+)[\'"]?', content, re.M)
    t = m.group(1).strip() if m else ''
    print(f"{os.path.basename(f)}: [{len(t)}] {t}")
