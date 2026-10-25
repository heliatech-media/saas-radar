import os
from pathlib import Path

config_path = Path("agents/config.py")
content = config_path.read_text(encoding="utf-8")

if "DEVTO_API_KEY" not in content:
    target = 'GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")'
    replacement = 'GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")\nDEVTO_API_KEY = os.getenv("DEVTO_API_KEY", "")'
    new_content = content.replace(target, replacement)
    config_path.write_text(new_content, encoding="utf-8")
    print("DEVTO_API_KEY added to agents/config.py")
else:
    print("DEVTO_API_KEY already present")
