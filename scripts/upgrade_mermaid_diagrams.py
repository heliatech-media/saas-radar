import glob
import re
import os

def clean_category(cat):
    if not cat:
        return "Intelligence"
    cat = cat.replace('&', '+').strip()
    if cat.lower().endswith('platform'):
        cat = cat[:-8].strip()
    if len(cat) > 28:
        cat = cat[:28].strip()
    return cat

def main():
    files = glob.glob('site/src/content/blog/*.md')
    print(f"Scanning {len(files)} files...")
    
    pattern = re.compile(
        r'```mermaid\s*\n\s*flowchart LR\s*\n\s*A\[Manual Bottleneck\] --> B\[(.*?) Engine\]\s*\n\s*B --> C\[Automated Workflow\]\s*\n\s*C --> D\[ROI Multiplier\]\s*\n\s*style B fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#030712\s*\n\s*style D fill:#d946ef,stroke:#c026d3,stroke-width:2px,color:#ffffff\s*\n\s*```',
        re.MULTILINE
    )
    
    upgraded = 0
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
            
        m = pattern.search(content)
        if m:
            tool_name = m.group(1).strip()
            
            # get category
            cat_match = re.search(r'category:\s*(.*)', content)
            raw_cat = cat_match.group(1).strip() if cat_match else "Intelligence"
            cat_clean = clean_category(raw_cat)
            
            replacement = f"""```mermaid
flowchart TD
    subgraph S1["PHASE 1: ENTERPRISE INGESTION & DATA FLOW"]
        direction LR
        A["⚙️ Legacy Friction<br/>Manual Overhead & Data Silos"] --> B["⚡ {tool_name} Core Engine<br/>Automated {cat_clean} Platform"]
    end
    subgraph S2["PHASE 2: ORCHESTRATION & IMPACT SURGE"]
        direction LR
        C["🔄 Continuous Pipeline<br/>Omnichannel Workflow Automation"] --> D["📈 Enterprise ROI Moat<br/>Maximized Velocity & Compound Yield"]
    end
    S1 -->|High-Speed Protocol| S2
    style B fill:#0c1425,stroke:#06b6d4,stroke-width:2.5px,color:#f8fafc
    style D fill:#0c1425,stroke:#10b981,stroke-width:2.5px,color:#f8fafc
```"""
            new_content = pattern.sub(replacement, content, count=1)
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(new_content)
            upgraded += 1
            
    print(f"Successfully upgraded {upgraded} markdown files with enterprise 2-tier architectural schemas!")

if __name__ == '__main__':
    main()
