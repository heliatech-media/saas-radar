import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

client_id = os.getenv("REDDIT_CLIENT_ID", "")
client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
username = os.getenv("REDDIT_USERNAME", "")
password = os.getenv("REDDIT_PASSWORD", "")

if not client_id or not client_secret:
    print("❌ REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET missing in .env")
    print("Please add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env")
    sys.exit(1)

try:
    import praw
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent="HeliaTechAutonomousAgent/1.0 by HeliaTech Media"
    )
    user = reddit.user.me()
    print(f"✅ Reddit Authenticated Successfully! Connected as: u/{user.name} (Karma: {user.link_karma + user.comment_karma})")
except Exception as e:
    print(f"❌ Reddit Authentication Failed: {e}")
    sys.exit(1)
