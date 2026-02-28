"""X (Twitter) scraper – sucht nach trending AI-Themen via API v2 Bearer Token."""

import os
import time
import requests
from datetime import datetime, timedelta, timezone

AI_QUERIES = [
    "AI OR LLM OR ChatGPT OR Claude OR Gemini lang:en -is:retweet",
    "OpenAI OR Anthropic OR \"machine learning\" lang:en -is:retweet",
    "\"artificial intelligence\" OR \"large language model\" lang:en -is:retweet",
]

HEADERS_TEMPLATE = {"Authorization": "Bearer {token}"}


def fetch(hours_back: int = 24) -> list[dict]:
    """
    Holt trending AI-Tweets via X API v2 (kostenloser Bearer Token).
    Gibt [] zurück wenn TWITTER_BEARER_TOKEN nicht gesetzt.
    """
    token = os.environ.get("TWITTER_BEARER_TOKEN")
    if not token:
        print("[X/Twitter] Kein Bearer Token – übersprungen.")
        return []

    headers = {"Authorization": f"Bearer {token}"}
    since = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    results = []
    seen_ids = set()

    for query in AI_QUERIES:
        try:
            params = {
                "query": query,
                "max_results": 10,
                "start_time": since,
                "tweet.fields": "public_metrics,author_id,created_at",
                "expansions": "author_id",
                "user.fields": "name,username",
            }
            resp = requests.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=15,
            )

            if resp.status_code == 429:
                print("[X/Twitter] Rate limit erreicht – übersprungen.")
                break
            if resp.status_code == 401:
                print("[X/Twitter] Ungültiger Bearer Token.")
                break
            if not resp.ok:
                continue

            data = resp.json()
            tweets = data.get("data", [])

            # Build user lookup
            users = {
                u["id"]: u
                for u in data.get("includes", {}).get("users", [])
            }

            for tweet in tweets:
                tid = tweet.get("id")
                if tid in seen_ids:
                    continue
                seen_ids.add(tid)

                metrics = tweet.get("public_metrics", {})
                engagement = (
                    metrics.get("like_count", 0)
                    + metrics.get("retweet_count", 0) * 2
                    + metrics.get("reply_count", 0)
                )

                # Nur relevante Tweets (mindestens etwas Engagement)
                if engagement < 5:
                    continue

                author = users.get(tweet.get("author_id"), {})
                username = author.get("username", "unknown")

                results.append({
                    "source": "X (Twitter)",
                    "text": tweet.get("text", "")[:280],
                    "url": f"https://x.com/{username}/status/{tid}",
                    "author": f"@{username}",
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "engagement": engagement,
                })

            time.sleep(1)

        except Exception as e:
            print(f"[X/Twitter] Fehler: {e}")
            continue

    results.sort(key=lambda x: x["engagement"], reverse=True)
    return results[:12]
