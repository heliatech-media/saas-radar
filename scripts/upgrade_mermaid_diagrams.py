import glob
import re

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
    
    # Matches either the previous subgraph format or legacy Manual Bottleneck format
    pattern = re.compile(
        r'```mermaid\s*\n\s*flowchart TD\s*\n\s*subgraph S1\[\"PHASE 1:.*?\"\]\s*\n\s*direction LR\s*\n\s*A\[\".*?\"\] --> B\[\"⚡ (.*?) Core Engine.*?\"\]\s*\n\s*end\s*\n\s*subgraph S2\[\"PHASE 2:.*?\"\]\s*\n\s*direction LR\s*\n\s*C\[\".*?\"\] --> D\[\".*?\"\]\s*\n\s*end\s*\n\s*S1 -->\|.*?\| S2\s*\n\s*style B.*?\n\s*style D.*?\n\s*```',
        re.MULTILINE
    )
    
    # Also fallback for any file that might still have flowchart LR Manual Bottleneck
    pattern_lr = re.compile(
        r'```mermaid\s*\n\s*flowchart LR\s*\n\s*A\[Manual Bottleneck\] --> B\[(.*?) Engine\]\s*\n\s*B --> C\[Automated Workflow\]\s*\n\s*C --> D\[ROI Multiplier\]\s*\n\s*style B.*?\n\s*style D.*?\n\s*```',
        re.MULTILINE
    )
    
    upgraded = 0
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()
            
        tool_name = None
        match_used = None
        
        m = pattern.search(content)
        if m:
            tool_name = m.group(1).strip()
            match_used = pattern
        else:
            m_lr = pattern_lr.search(content)
            if m_lr:
                tool_name = m_lr.group(1).strip()
                match_used = pattern_lr
                
        if tool_name and match_used:
            cat_match = re.search(r'category:\s*(.*)', content)
            raw_cat = cat_match.group(1).strip() if cat_match else "Intelligence"
            cat_clean = clean_category(raw_cat)
            
            replacement = f"""```mermaid
flowchart TD
    Inp["⚙️ Inbound Friction: Manual Bottlenecks & Siloed Data"]
    Eng["⚡ {tool_name} Platform: Automated {cat_clean} Core"]
    Out1["🔄 Continuous Pipeline: Omnichannel Workflow Sync"]
    Out2["📈 Enterprise Value: Scaled Velocity & Compound ROI"]
    Inp -->|Ingestion & Webhooks| Eng
    Eng -->|Autonomous Execution| Out1
    Eng -->|Performance Lift| Out2
    style Inp fill:#0f172a,stroke:#475569,stroke-width:2px,color:#f8fafc
    style Eng fill:#0c1425,stroke:#06b6d4,stroke-width:2.5px,color:#f8fafc
    style Out1 fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#f8fafc
    style Out2 fill:#0c1425,stroke:#10b981,stroke-width:2.5px,color:#f8fafc
```"""
            new_content = match_used.sub(replacement, content, count=1)
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(new_content)
            upgraded += 1
            
    print(f"Successfully upgraded {upgraded} markdown files to 3-tier Hub & Spoke architecture!")

if __name__ == '__main__':
    main()
