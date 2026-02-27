"""Reddit scraper – nutzt die öffentliche JSON-API (kein API-Key nötig)."""

import time
import requests
from datetime import datetime, timedelta, timezone

SUBREDDITS = [
    "artificial",
    "MachineLearning",
    "LocalLLaMA",
    "AINews",
    "OpenAI",
    "ChatGPT",
    "singularity",
    "StableDiffusion",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 ai-news-aggregator/1.0",
}


def fetch(time_filter: str = "day", limit: int = 10) -> list[dict]:
    """
    time_filter: 'day' für täglich, 'week' für wöchentlich
    Nutzt reddit.com/r/SUBREDDIT/top.json — kein API-Key erforderlich.
    """
    results = []
    seen_ids = set()

    for sub in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{sub}/top.json"
            params = {"t": time_filter, "limit": limit}
            resp = requests.get(url, headers=HEADERS, params=params, timeout=15)

            if resp.status_code == 429:
                time.sleep(5)
                continue
            if not resp.ok:
                continue

            data = resp.json()
            posts = data.get("data", {}).get("children", [])

            for child in posts:
                post = child.get("data", {})
                post_id = post.get("id")
                if not post_id or post_id in seen_ids:
                    continue
                seen_ids.add(post_id)

                score = post.get("score", 0)
                if score < 20:
                    continue

                selftext = post.get("selftext", "")
                if selftext and len(selftext) > 20:
                    selftext = selftext[:300].strip()

                results.append({
                    "source": "Reddit",
                    "subreddit": sub,
                    "title": post.get("title", ""),
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "external_url": post.get("url", ""),
                    "score": score,
                    "comments": post.get("num_comments", 0),
                    "selftext_preview": selftext,
                })

            time.sleep(1)  # Reddit rate limit schonen

        except Exception as e:
            print(f"[Reddit] {sub}: {e}")
            continue

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:20]
