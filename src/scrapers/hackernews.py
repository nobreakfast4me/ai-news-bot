"""Hacker News scraper – uses Algolia HN API (no auth required)."""

import time
import requests
from datetime import datetime, timedelta, timezone

AI_KEYWORDS = [
    "LLM", "AI", "machine learning", "GPT", "Claude", "Gemini", "artificial intelligence",
    "neural network", "deep learning", "OpenAI", "Anthropic", "transformer",
    "diffusion", "reinforcement learning", "RAG", "fine-tuning", "inference",
    "agent", "multimodal", "embedding", "vector database",
]

def fetch(hours_back: int = 24) -> list[dict]:
    """Fetch top AI/ML stories from Hacker News via Algolia API."""
    try:
        since_timestamp = int((datetime.now(timezone.utc) - timedelta(hours=hours_back)).timestamp())

        results = []
        seen_ids = set()

        for keyword in AI_KEYWORDS[:10]:  # limit to avoid too many requests
            try:
                url = "https://hn.algolia.com/api/v1/search"
                params = {
                    "query": keyword,
                    "tags": "story",
                    "numericFilters": f"created_at_i>{since_timestamp},points>10",
                    "hitsPerPage": 10,
                }
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                for hit in data.get("hits", []):
                    story_id = hit.get("objectID")
                    if story_id in seen_ids:
                        continue
                    seen_ids.add(story_id)

                    title = hit.get("title", "")
                    if not title:
                        continue

                    results.append({
                        "source": "Hacker News",
                        "title": title,
                        "url": hit.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                        "hn_url": f"https://news.ycombinator.com/item?id={story_id}",
                        "score": hit.get("points", 0),
                        "comments": hit.get("num_comments", 0),
                        "author": hit.get("author", ""),
                    })
                time.sleep(0.2)
            except Exception:
                continue

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:15]

    except Exception as e:
        print(f"[HackerNews] Error: {e}")
        return []
