import glob
import os
import yaml

files = glob.glob('site/src/content/blog/*.md')
print(f"Total blog files: {len(files)}")

desc_lengths = []
for f in sorted(files):
    content = open(f, encoding='utf-8', errors='ignore').read()
    # parse frontmatter
    parts = content.split('---', 2)
    if len(parts) >= 3:
        try:
            data = yaml.safe_load(parts[1])
            d = data.get('description', '') if isinstance(data, dict) else ''
            desc_lengths.append((len(d), d, os.path.basename(f)))
        except Exception as e:
            pass

print(f"Parsed {len(desc_lengths)} files with PyYAML")
print(f"Average desc length: {sum(l for l, d, f in desc_lengths) / len(desc_lengths):.1f}")
print(f"Descriptions < 120 chars: {len([l for l, d, f in desc_lengths if l < 120])}")
print(f"Descriptions 120-160 chars: {len([l for l, d, f in desc_lengths if 120 <= l <= 160])}")
print(f"Descriptions > 160 chars: {len([l for l, d, f in desc_lengths if l > 160])}")
print("\nSample real descriptions:")
for l, d, f in sorted(desc_lengths)[:10]:
    print(f"[{l}] {f}: {d}")
