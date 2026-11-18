import os
import glob
import xml.etree.ElementTree as ET
from pathlib import Path

content_dir = Path("site/src/content")
public_dir = Path("site/public")

issues = []
checked = 0

for md_file in content_dir.glob("**/*.md"):
    checked += 1
    content = md_file.read_text(encoding="utf-8")
    image_line = None
    slug = md_file.stem
    tool_slug = None

    for line in content.splitlines()[:40]:
        line_clean = line.strip()
        if line_clean.startswith("image:"):
            image_line = line_clean.split("image:", 1)[1].strip().strip("\"'")
        if line_clean.startswith("tool_slug:"):
            tool_slug = line_clean.split("tool_slug:", 1)[1].strip().strip("\"'")

    target_img = image_line or f"/images/blog/{tool_slug or slug}.svg"
    local_path = public_dir / target_img.lstrip("/")

    # Check if file exists
    if not local_path.exists():
        # Check if png exists instead or svg exists instead
        png_path = local_path.with_suffix(".png")
        svg_path = local_path.with_suffix(".svg")
        if not png_path.exists() and not svg_path.exists():
            issues.append((str(md_file), f"Missing image: {target_img} (neither {png_path.name} nor {svg_path.name} found)"))
    else:
        if local_path.suffix.lower() == ".svg":
            try:
                ET.parse(local_path)
            except Exception as e:
                issues.append((str(md_file), f"Invalid SVG XML in {target_img}: {e}"))

print(f"Checked {checked} markdown articles/reviews.")
print(f"Found {len(issues)} issues:")
for f, issue in issues:
    print(f" ❌ {f}: {issue}")
