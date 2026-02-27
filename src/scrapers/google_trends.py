"""Google Trends scraper – fetches trending AI-related search terms."""

import time
from pytrends.request import TrendReq

AI_SEED_KEYWORDS = [
    "ChatGPT", "AI tools", "LLM", "artificial intelligence",
    "Claude AI", "Gemini AI", "Midjourney", "Stable Diffusion",
    "AI agent", "machine learning",
]


def fetch(timeframe: str = "now 1-d") -> list[dict]:
    """
    timeframe: 'now 1-d' for last 24h, 'now 7-d' for last 7 days
    Returns trending keywords and related queries.
    """
    try:
        pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
        results = []

        # Get interest over time for seed keywords (batches of 5)
        for i in range(0, len(AI_SEED_KEYWORDS), 5):
            batch = AI_SEED_KEYWORDS[i:i + 5]
            try:
                pytrends.build_payload(batch, timeframe=timeframe, geo="")
                interest = pytrends.interest_over_time()

                if interest is not None and not interest.empty:
                    # Get average interest for each keyword
                    interest = interest.drop(columns=["isPartial"], errors="ignore")
                    avg = interest.mean().to_dict()
                    for kw, score in avg.items():
                        if score > 5:
                            results.append({
                                "source": "Google Trends",
                                "keyword": kw,
                                "interest_score": round(float(score), 1),
                            })

                time.sleep(2)  # respect rate limits

            except Exception:
                time.sleep(5)
                continue

        # Also get trending searches (real-time)
        try:
            trending = pytrends.trending_searches(pn="united_states")
            ai_trending = []
            ai_terms = {"ai", "gpt", "llm", "claude", "gemini", "openai",
                       "anthropic", "chatgpt", "midjourney", "sora", "robot",
                       "machine learning", "neural", "deepmind", "nvidia"}
            for term in trending[0].tolist()[:50]:
                if any(t in term.lower() for t in ai_terms):
                    ai_trending.append({
                        "source": "Google Trends Realtime",
                        "keyword": term,
                        "interest_score": 100,
                    })
            results.extend(ai_trending[:5])
        except Exception:
            pass

        # Sort by interest score
        results.sort(key=lambda x: x["interest_score"], reverse=True)
        return results[:15]

    except Exception as e:
        print(f"[Google Trends] Error: {e}")
        return []
