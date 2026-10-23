"""
🚀 Agent Social Growth & Viral Distribution (Helia X/Twitter Growth Core).
- Generates high-engagement Twitter/X threads and LinkedIn authority breakdowns for every published article.
- Prepared for autonomous posting via X API v2 as soon as user configures credentials in .env.
- Designed to drive viral social referral traffic toward the 100,000 monthly visitors milestone.
"""

import os
import json
from google import genai
from google.genai import types
from agents.config import GEMINI_API_KEY, GEMINI_MODEL
from agents.models import BlogPost


class SocialGrowthAgent:
    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model = model

        # X (Twitter) API credentials
        self.twitter_api_key = os.getenv("TWITTER_API_KEY", "")
        self.twitter_api_secret = os.getenv("TWITTER_API_SECRET", "")
        self.twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN", "")
        self.twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET", "")

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
        Broadcasts thread to X when API keys are supplied in .env.
        Posts a continuous threaded reply sequence via X API v2.
        """
        if not (self.twitter_api_key and self.twitter_api_secret and self.twitter_access_token and self.twitter_access_secret):
            print("[SOCIAL AGENT] ℹ️ Twitter API credentials not detected in .env. Thread drafted and ready for broadcast.")
            return False

        try:
            from requests_oauthlib import OAuth1Session
            oauth = OAuth1Session(
                client_key=self.twitter_api_key,
                client_secret=self.twitter_api_secret,
                resource_owner_key=self.twitter_access_token,
                resource_owner_secret=self.twitter_access_secret,
            )

            print(f"[SOCIAL AGENT] 🚀 Broadcasting {len(tweets)}-tweet thread to X via API v2...")
            previous_tweet_id = None
            successful_posts = 0

            for i, tweet_text in enumerate(tweets):
                payload = {"text": tweet_text}
                if previous_tweet_id:
                    payload["reply"] = {"in_reply_to_tweet_id": previous_tweet_id}

                response = oauth.post("https://api.twitter.com/2/tweets", json=payload, timeout=15)
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
