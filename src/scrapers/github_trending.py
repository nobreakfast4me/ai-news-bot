"""GitHub Trending scraper – fetches trending AI/ML repositories."""

import requests
from bs4 import BeautifulSoup

AI_TOPICS = ["artificial-intelligence", "machine-learning", "deep-learning",
             "llm", "large-language-model", "generative-ai"]

AI_KEYWORDS = {"ai", "llm", "gpt", "neural", "ml", "deep learning",
               "machine learning", "diffusion", "transformer", "nlp",
               "inference", "fine-tun", "rag", "embedding", "agent",
               "generative", "stable diffusion", "openai", "anthropic",
               "langchain", "llamaindex", "huggingface"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ai-news-bot/1.0)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def _is_ai_related(name: str, description: str) -> bool:
    text = (name + " " + description).lower()
    return any(kw in text for kw in AI_KEYWORDS)


def fetch(since: str = "daily") -> list[dict]:
    """
    since: 'daily' or 'weekly'
    Returns trending AI/ML GitHub repositories.
    """
    try:
        url = f"https://github.com/trending?since={since}&spoken_language_code=en"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        repo_items = soup.select("article.Box-row")

        results = []
        for item in repo_items:
            try:
                # Repository name
                h2 = item.select_one("h2 a")
                if not h2:
                    continue
                repo_path = h2.get("href", "").strip("/")
                repo_name = repo_path.replace("/", " / ")

                # Description
                desc_el = item.select_one("p")
                description = desc_el.get_text(strip=True) if desc_el else ""

                # Skip non-AI repos
                if not _is_ai_related(repo_name, description):
                    continue

                # Stars total
                stars_el = item.select_one("a[href$='/stargazers']")
                stars_text = stars_el.get_text(strip=True) if stars_el else "0"
                stars_text = stars_text.replace(",", "").replace("k", "000").strip()
                try:
                    stars = int(stars_text.split()[0])
                except (ValueError, IndexError):
                    stars = 0

                # Stars today/this week
                stars_period_el = item.select_one("span.d-inline-block.float-sm-right")
                stars_period = stars_period_el.get_text(strip=True) if stars_period_el else ""

                # Language
                lang_el = item.select_one("span[itemprop='programmingLanguage']")
                language = lang_el.get_text(strip=True) if lang_el else ""

                results.append({
                    "source": "GitHub Trending",
                    "name": repo_name,
                    "url": f"https://github.com/{repo_path}",
                    "description": description,
                    "stars": stars,
                    "stars_period": stars_period,
                    "language": language,
                })
            except Exception:
                continue

        return results[:15]

    except Exception as e:
        print(f"[GitHub Trending] Error: {e}")
        return []
