"""
🚀 Agent Social Growth & Viral Distribution (Helia X/Twitter Growth Core).
- Generates high-engagement Twitter/X threads and LinkedIn authority breakdowns for every published article.
- Prepared for autonomous posting via X API v2 as soon as user configures credentials in .env.
- Designed to drive viral social referral traffic toward the 100,000 monthly visitors milestone.
"""

import os
import sys
import json
from pathlib import Path
from google import genai
from google.genai import types
from agents.config import GEMINI_API_KEY, GEMINI_MODEL
from agents.models import BlogPost

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class SocialGrowthAgent:
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = model

        # X (Twitter) API credentials & Safety Lock
        self.twitter_broadcast_enabled = os.getenv("TWITTER_BROADCAST_ENABLED", "false").lower() == "true"
        self.twitter_api_key = os.getenv("TWITTER_API_KEY", "")
        self.twitter_api_secret = os.getenv("TWITTER_API_SECRET", "")
        self.twitter_client_id = os.getenv("TWITTER_CLIENT_ID", "")
        self.twitter_client_secret = os.getenv("TWITTER_CLIENT_SECRET", "")
        self.twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET", "")
        self.twitter_refresh_token = os.getenv("TWITTER_REFRESH_TOKEN", "")

        # LinkedIn API credentials & Safety Lock
        self.linkedin_broadcast_enabled = os.getenv("LINKEDIN_BROADCAST_ENABLED", "false").lower() == "true"
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
        self.linkedin_access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.linkedin_author_urn = os.getenv("LINKEDIN_AUTHOR_URN", "")

    def refresh_oauth2_token(self) -> bool:
        """Refreshes the OAuth 2.0 access token using the 6-month refresh token."""
        if not (self.twitter_client_id and self.twitter_client_secret and self.twitter_refresh_token):
            return False

        try:
            import requests
            from requests.auth import HTTPBasicAuth
            from pathlib import Path
            import re

            response = requests.post(
                "https://api.twitter.com/2/oauth2/token",
                auth=HTTPBasicAuth(self.twitter_client_id, self.twitter_client_secret),
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.twitter_refresh_token,
                    "client_id": self.twitter_client_id,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15,
            )
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get("access_token")
                new_refresh_token = data.get("refresh_token")
                if new_access_token:
                    self.twitter_access_token = new_access_token
                    os.environ["TWITTER_ACCESS_TOKEN"] = new_access_token
                    if new_refresh_token:
                        self.twitter_refresh_token = new_refresh_token
                        os.environ["TWITTER_REFRESH_TOKEN"] = new_refresh_token

                    # Persist back to .env
                    env_path = Path(__file__).resolve().parent.parent / ".env"
                    if env_path.exists():
                        content = env_path.read_text(encoding="utf-8")
                        content = re.sub(r'TWITTER_ACCESS_TOKEN=.*', f'TWITTER_ACCESS_TOKEN={new_access_token}', content)
                        if new_refresh_token:
                            content = re.sub(r'TWITTER_REFRESH_TOKEN=.*', f'TWITTER_REFRESH_TOKEN={new_refresh_token}', content)
                        env_path.write_text(content, encoding="utf-8")

                    print("[SOCIAL AGENT] 🔄 Successfully refreshed X OAuth 2.0 access token!")
                    return True
            else:
                print(f"[SOCIAL AGENT] ⚠️ Token refresh error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[SOCIAL AGENT] ❌ Exception during token refresh: {e}")
            return False

    def craft_viral_x_thread(self, post: BlogPost) -> list[str]:
        """Crafts a 4-tweet viral thread optimized for X algorithms to maximize clicks to the blog."""
        prompt = f"""
You are a viral B2B tech growth hacker and founder on X (Twitter).
Write a high-converting, curiosity-inducing 4-tweet thread breaking down this software investigation:

Article Title: {post.title}
Tool: {post.tool_slug}
Key Takeaways: {', '.join(post.tldr)}
Live Article URL: https://heliatech.online/blog/{post.slug}

Tweet Guidelines:
1. Tweet 1 (Hook): Provocative hook addressing a major enterprise problem or founder mistake. No hashtags in tweet 1. Under 240 chars.
2. Tweet 2: The hidden breakdown / insight that nobody talks about. Under 240 chars.
3. Tweet 3: The practical 15-minute takeaway / result. Under 240 chars.
4. Tweet 4 (CTA): Read the full investigative breakdown and masterclass with zero fluff at the live URL.

Output format:
Return ONLY a valid JSON array of strings: ["tweet 1", "tweet 2", "tweet 3", "tweet 4"].
No markdown fences or commentary.
"""
        if not self.client:
            return [
                f"How {post.tool_slug.capitalize()} quietly disrupted enterprise software in 2026. A breakdown of their secret playbook 🧵👇",
                f"Most companies lose hours juggling fragmented point tools. Here is why modern teams are consolidating onto {post.tool_slug.capitalize()}.",
                f"In our 15-minute benchmark test, automating this single pipeline unlocked $950/mo in recovered team capacity.",
                f"Read our full architectural teardown and hands-on guide here: https://heliatech.online/blog/{post.slug}"
            ]

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    response_mime_type="application/json"
                )
            )
            tweets = json.loads(response.text)
            return tweets if isinstance(tweets, list) else []
        except Exception:
            return [
                f"Why {post.tool_slug.capitalize()} is taking over modern tech stacks in 2026: https://heliatech.online/blog/{post.slug}"
            ]

    def broadcast_thread_to_x(self, tweets: list[str]) -> bool:
        """
        Broadcasts thread to X when API keys are supplied in .env and TWITTER_BROADCAST_ENABLED=true.
        Supports both OAuth 1.0a (API Key + Secret + Access Token + Secret)
        and OAuth 2.0 User Token (Bearer token with tweet.write scope).
        """
        if not self.twitter_broadcast_enabled:
            print("[SOCIAL AGENT] 🔒 X/Twitter broadcast is on STANDBY (TWITTER_BROADCAST_ENABLED=false). No tweets published.")
            return False

        has_oauth1 = bool(self.twitter_api_key and self.twitter_api_secret and self.twitter_access_token and self.twitter_access_secret)
        has_oauth2_user = bool(self.twitter_access_token and not self.twitter_access_secret)

        if not (has_oauth1 or has_oauth2_user):
            print("[SOCIAL AGENT] ℹ️ Twitter API credentials not detected in .env. Thread drafted and ready for broadcast.")
            return False

        try:
            import requests

            if has_oauth1:
                from requests_oauthlib import OAuth1Session
                session = OAuth1Session(
                    client_key=self.twitter_api_key,
                    client_secret=self.twitter_api_secret,
                    resource_owner_key=self.twitter_access_token,
                    resource_owner_secret=self.twitter_access_secret,
                )
            else:
                session = requests.Session()
                session.headers.update({
                    "Authorization": f"Bearer {self.twitter_access_token}",
                    "Content-Type": "application/json"
                })

            print(f"[SOCIAL AGENT] 🚀 Broadcasting {len(tweets)}-tweet thread to X via API v2...")
            previous_tweet_id = None
            successful_posts = 0

            for i, tweet_text in enumerate(tweets):
                payload = {"text": tweet_text}
                if previous_tweet_id:
                    payload["reply"] = {"in_reply_to_tweet_id": previous_tweet_id}

                response = session.post("https://api.twitter.com/2/tweets", json=payload, timeout=15)
                if response.status_code == 401 and has_oauth2_user:
                    print("[SOCIAL AGENT] ⚠️ Token expired (401). Triggering automatic OAuth 2.0 renewal...")
                    if self.refresh_oauth2_token():
                        session.headers["Authorization"] = f"Bearer {self.twitter_access_token}"
                        response = session.post("https://api.twitter.com/2/tweets", json=payload, timeout=15)

                if response.status_code in [200, 201]:
                    data = response.json().get("data", {})
                    previous_tweet_id = data.get("id")
                    successful_posts += 1
                else:
                    print(f"[SOCIAL AGENT] ⚠️ Failed on tweet {i+1}: {response.status_code} - {response.text}")
                    break

            if successful_posts > 0:
                print(f"[SOCIAL AGENT] ✅ Successfully published {successful_posts} tweets to X in sequence!")
                return True
            return False
        except Exception as e:
            print(f"[SOCIAL AGENT] ❌ Exception during X broadcast: {e}")
            return False

    def craft_linkedin_authority_post(self, post: BlogPost) -> str:
        """
        Drafts a high-impact B2B thought-leadership post for LinkedIn:
        - Strong executive hook
        - 3 key bullet points with metric takeaways
        - Clear CTA linking to the full HeliaTech investigation
        - Clean LinkedIn hashtag block
        """
        prompt = f"""
You are the Chief B2B Growth Strategist and Media Director for HELIA TECH (heliatech.online).
Write an elite, high-retention LinkedIn thought-leadership post based on this software investigation:

Article Title: {post.title}
Software Tool: {post.tool_slug.capitalize()}
Category: {post.category}
Key Insights: {', '.join(post.tldr)}
Article URL: https://heliatech.online/blog/{post.slug}

Formatting & Tone Directives:
1. Short, punchy sentences with ample white space (1-2 lines per paragraph for mobile readability).
2. Start with an arresting executive question or counter-intuitive industry fact.
3. Include 3 bullet points using symbols (→, ▹, or ⚡) breaking down the ROI or velocity impact.
4. Conclude with an invitation to read the full benchmark dossier at the article URL.
5. Add 3 to 5 targeted B2B hashtags (e.g. #SaaS #Productivity #AI #Automation #TechStrategy).
6. 100% native professional American English.

Reply ONLY with the text of the LinkedIn post. No commentary.
"""
        if not self.client:
            return f"""Most engineering and operations leaders are still evaluating software based on legacy 2022 metrics.

Here is the reality we observed in our latest forensic benchmark of {post.tool_slug.capitalize()}:

⚡ Context switching costs teams up to 40% of productive weekly output.
⚡ Point tools create data silos that throttle enterprise agility.
⚡ Consolidating workflows onto an integrated engine recovers hundreds of hours each quarter.

We just published our complete architectural teardown and hands-on workshop on the HeliaTech Observatory:

👉 Read the full investigation here: https://heliatech.online/blog/{post.slug}

#SaaS #EnterpriseTech #Automation #Productivity #HeliaTech"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7)
            )
            return response.text.strip()
        except Exception as e:
            print(f"[SOCIAL AGENT] ⚠️ Error generating LinkedIn post: {e}")
            return f"Read our latest B2B software breakdown on {post.tool_slug.capitalize()}: https://heliatech.online/blog/{post.slug}"

    def broadcast_post_to_linkedin(self, post_text: str) -> bool:
        """
        Publishes a post to LinkedIn via the LinkedIn REST API / v2 API.
        Safety lock: only sends when LINKEDIN_BROADCAST_ENABLED=true.
        """
        if not self.linkedin_broadcast_enabled:
            print("[SOCIAL AGENT] 🔒 LinkedIn broadcast is on STANDBY (LINKEDIN_BROADCAST_ENABLED=false). Post drafted but not sent.")
            return False

        if not self.linkedin_access_token:
            print("[SOCIAL AGENT] ℹ️ LinkedIn Access Token missing in .env.")
            return False

        try:
            import requests

            # Auto-detect author URN if not explicitly configured in .env
            author_urn = self.linkedin_author_urn
            if not author_urn:
                try:
                    u_res = requests.get(
                        "https://api.linkedin.com/v2/userinfo",
                        headers={"Authorization": f"Bearer {self.linkedin_access_token}"},
                        timeout=10
                    )
                    if u_res.status_code == 200:
                        sub = u_res.json().get("sub")
                        if sub:
                            author_urn = f"urn:li:person:{sub}"
                            print(f"[SOCIAL AGENT] 👤 Auto-detected LinkedIn author: {author_urn}")
                except Exception:
                    pass

            if not author_urn:
                print("[SOCIAL AGENT] ℹ️ Unable to determine LinkedIn author URN. Please specify LINKEDIN_AUTHOR_URN in .env.")
                return False

            url = "https://api.linkedin.com/v2/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.linkedin_access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": post_text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                print("[SOCIAL AGENT] ✅ Successfully published post to LinkedIn!")
                return True
            else:
                print(f"[SOCIAL AGENT] ⚠️ LinkedIn post error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[SOCIAL AGENT] ❌ Exception during LinkedIn broadcast: {e}")
            return False
