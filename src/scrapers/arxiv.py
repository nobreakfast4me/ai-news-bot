"""ArXiv scraper – fetches latest AI/ML research papers."""

import arxiv
from datetime import datetime, timedelta, timezone

CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE"]

def fetch(days_back: int = 1) -> list[dict]:
    """Fetch recent papers from ArXiv AI/ML categories."""
    try:
        since = datetime.now(timezone.utc) - timedelta(days=days_back)
        results = []
        seen_ids = set()

        client = arxiv.Client(page_size=20, num_retries=3)

        for category in CATEGORIES:
            try:
                search = arxiv.Search(
                    query=f"cat:{category}",
                    max_results=15,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending,
                )

                for paper in client.results(search):
                    if paper.entry_id in seen_ids:
                        continue

                    # Filter to recent papers
                    if paper.published and paper.published < since:
                        break

                    seen_ids.add(paper.entry_id)

                    authors = [a.name for a in paper.authors[:3]]
                    author_str = ", ".join(authors)
                    if len(paper.authors) > 3:
                        author_str += " et al."

                    results.append({
                        "source": "ArXiv",
                        "category": category,
                        "title": paper.title.strip(),
                        "url": paper.entry_id,
                        "pdf_url": paper.pdf_url,
                        "authors": author_str,
                        "abstract": paper.summary[:400].strip(),
                        "published": paper.published.strftime("%Y-%m-%d") if paper.published else "",
                    })
            except Exception:
                continue

        return results[:20]

    except Exception as e:
        print(f"[ArXiv] Error: {e}")
        return []
