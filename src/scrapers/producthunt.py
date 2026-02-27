"""ProductHunt scraper – fetches new AI tools and products."""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ai-news-bot/1.0)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch() -> list[dict]:
    """Fetch top AI products from ProductHunt."""
    try:
        # ProductHunt AI topic page
        url = "https://www.producthunt.com/topics/artificial-intelligence"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

        # Try to find product cards (ProductHunt structure may vary)
        # Looking for product list items
        product_cards = soup.find_all("li", {"data-test": True}) or \
                        soup.select('[data-test="post-item"]') or \
                        soup.select("section li") or \
                        soup.select("ul li")

        for card in product_cards[:20]:
            try:
                # Title
                title_el = card.find(["h3", "h2", "strong"]) or \
                           card.select_one('[class*="title"]') or \
                           card.select_one('[class*="name"]')
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not title or len(title) < 3:
                    continue

                # Link
                link_el = card.find("a", href=True)
                if not link_el:
                    continue
                href = link_el["href"]
                if href.startswith("/"):
                    href = "https://www.producthunt.com" + href
                if "producthunt.com" not in href:
                    continue

                # Description
                desc_el = card.find("p") or card.select_one('[class*="tagline"]')
                description = desc_el.get_text(strip=True) if desc_el else ""

                # Upvotes
                vote_el = card.select_one('[class*="vote"]') or \
                          card.select_one('button[class*="voteButton"]')
                votes = 0
                if vote_el:
                    vote_text = vote_el.get_text(strip=True).replace(",", "")
                    try:
                        votes = int("".join(filter(str.isdigit, vote_text)) or "0")
                    except ValueError:
                        votes = 0

                if len(results) < 15:
                    results.append({
                        "source": "ProductHunt",
                        "title": title,
                        "url": href,
                        "description": description[:200],
                        "upvotes": votes,
                    })
            except Exception:
                continue

        if not results:
            # Fallback: scrape today's featured products
            results = _fetch_daily_digest()

        return results[:12]

    except Exception as e:
        print(f"[ProductHunt] Error: {e}")
        return []


def _fetch_daily_digest() -> list[dict]:
    """Fallback: fetch from ProductHunt homepage."""
    try:
        url = "https://www.producthunt.com"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        ai_keywords = {"ai", "gpt", "llm", "artificial intelligence", "machine learning",
                      "neural", "automation", "chatbot", "image generation", "claude",
                      "openai", "generative"}

        for a_tag in soup.find_all("a", href=True)[:100]:
            href = a_tag.get("href", "")
            if "/posts/" not in href:
                continue
            title = a_tag.get_text(strip=True)
            if not title or len(title) < 5:
                continue
            # Check if AI related
            if any(kw in title.lower() for kw in ai_keywords):
                full_url = "https://www.producthunt.com" + href if href.startswith("/") else href
                results.append({
                    "source": "ProductHunt",
                    "title": title,
                    "url": full_url,
                    "description": "",
                    "upvotes": 0,
                })

        # Deduplicate by URL
        seen = set()
        unique = []
        for r in results:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique.append(r)
        return unique[:10]
    except Exception:
        return []
