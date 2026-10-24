import re
import sys
from pathlib import Path

# Ensure UTF-8 on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BLOG_DIR = Path('site/src/content/blog')

def heal_article(file_path: Path) -> bool:
    content = file_path.read_text(encoding='utf-8')
    original = content

    # 1. Clean repeated Executive Takeaway before HeliaTech Benchmark Access
    content = re.sub(
        r'(\s*\*{0,2}Executive Takeaway:\*{0,2})+\s*(\*{0,2}HeliaTech Benchmark Access:\*{0,2})',
        r' \2',
        content
    )

    # 2. Clean repeated Executive Takeaway in general
    content = re.sub(r'(\*{0,2}Executive Takeaway:\*{0,2}\s*){2,}', '**Executive Takeaway:** ', content)

    # 3. Clean stacked [!NOTE] / [!TIP] / [!WARNING] tags
    content = re.sub(r'(>\s*\[!(NOTE|TIP|WARNING)\]\s*\n)+', '> [!TIP]\n', content)

    # 4. Collapse repeated consecutive Benchmark Access blocks
    # e.g., (> [!TIP]\n> **HeliaTech Benchmark Access:**[^\n]+\n(\s*\n)?)+
    def collapse_benchmark(match):
        block = match.group(0)
        # Extract the last clean benchmark access line
        m = re.findall(r'> \*\*HeliaTech Benchmark Access:\*\*[^\n]+', block)
        if m:
            return f"> [!TIP]\n{m[-1]}\n\n"
        return block

    content = re.sub(
        r'(>\s*\[!TIP\]\s*\n>\s*\*\*HeliaTech Benchmark Access:\*\*[^\n]+\n(\s*\n)?){2,}',
        collapse_benchmark,
        content
    )

    # 5. Clean any lingering double alert headers inside blockquotes
    content = re.sub(r'>\s*\[!(NOTE|TIP|WARNING)\]\s*\n>\s*\[!(NOTE|TIP|WARNING)\]\s*\n', r'> [!TIP]\n', content)

    # 6. Clean consecutive empty blockquotes
    content = re.sub(r'(>\s*\n){2,}', '> \n', content)

    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

def main():
    print(f"Scanning {BLOG_DIR} for article typesetting artifacts...")
    healed = 0
    total = 0
    for f in sorted(BLOG_DIR.glob('*.md')):
        total += 1
        if heal_article(f):
            print(f"  ✓ Healed: {f.name}")
            healed += 1

    print(f"\nHealing complete! {healed}/{total} articles cleansed and restored to pristine typography.")

if __name__ == '__main__':
    main()
