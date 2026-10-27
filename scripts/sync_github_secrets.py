"""
Synchronize all production environment variables from .env to GitHub Actions Secrets.
Uses GitHub REST API and libsodium asymmetric encryption.
Retrieves GitHub token dynamically from Git Credential Helper or GITHUB_TOKEN env var.
"""

import os
import sys
import json
import subprocess
import urllib.request
from base64 import b64encode
from pathlib import Path
from nacl import encoding, public

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent

def get_github_token() -> str:
    """Dynamically retrieves GitHub token from environment or Git Credential Manager."""
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n",
            capture_output=True,
            text=True,
            check=True
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception as e:
        print(f"Could not read from credential helper: {e}")
    return ""

def load_env(env_path: Path):
    env_vars = {}
    if not env_path.exists():
        return env_vars
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            v = v.strip().strip('"\'')
            if v:
                env_vars[k.strip()] = v
    return env_vars

def get_repo_public_key(token: str, repo: str):
    url = f"https://api.github.com/repos/{repo}/actions/secrets/public-key"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.github+json"
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    pk = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def put_secret(token: str, repo: str, secret_name: str, encrypted_val: str, key_id: str):
    url = f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}"
    payload = json.dumps({
        "encrypted_value": encrypted_val,
        "key_id": key_id
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.github+json"
    }, method="PUT")
    with urllib.request.urlopen(req) as resp:
        return resp.status in (201, 204)

def main():
    token = get_github_token()
    if not token:
        print("Error: No GitHub token found in environment or credential manager.")
        sys.exit(1)

    repo = "heliatech-media/saas-radar"
    print(f"Connecting to {repo}...")
    pk_info = get_repo_public_key(token, repo)
    key_id = pk_info["key_id"]
    public_key = pk_info["key"]
    print(f"Retrieved Repository Public Key ID: {key_id}")
    
    env_vars = load_env(ROOT_DIR / ".env")
    print(f"Loaded {len(env_vars)} environment variables from .env")
    
    target_secrets = [
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
        "CLOUDFLARE_API_TOKEN",
        "CLOUDFLARE_ZONE_ID",
        "CLOUDFLARE_ACCOUNT_ID",
        "CLOUDFLARE_WEB_ANALYTICS_TOKEN",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "DEVTO_API_KEY",
        "LINKEDIN_CLIENT_ID",
        "LINKEDIN_CLIENT_SECRET",
        "LINKEDIN_ACCESS_TOKEN",
        "LINKEDIN_AUTHOR_URN",
        "LINKEDIN_BROADCAST_ENABLED",
        "PARTNERSTACK_API_KEY",
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_BEARER_TOKEN",
        "TWITTER_CLIENT_ID",
        "TWITTER_CLIENT_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_REFRESH_TOKEN",
        "SENTINEL_PASSWORD"
    ]
    
    success_count = 0
    for name in target_secrets:
        if name in env_vars:
            val = env_vars[name]
            enc = encrypt_secret(public_key, val)
            if put_secret(token, repo, name, enc, key_id):
                print(f"  Synced secret: {name}")
                success_count += 1
            else:
                print(f"  Failed to set secret: {name}")
        else:
            print(f"  Secret {name} not found in .env (skipped)")
            
    print(f"Successfully provisioned {success_count} secrets to GitHub Actions!")

if __name__ == "__main__":
    main()
