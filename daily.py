#!/usr/bin/env python3
"""Daily AI News Bot – sammelt Daten der letzten 24h und schickt Briefing via Telegram."""

import sys
import os
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.scrapers import reddit, hackernews, arxiv, github_trending, google_trends, producthunt
from src import summarizer, telegram_sender


def run():
    print("🤖 AI Daily Briefing Bot gestartet...")
    date_str = datetime.now(timezone.utc).strftime("%d.%m.%Y")

    # Run all scrapers in parallel
    results = {}
    scrapers = {
        "reddit": lambda: reddit.fetch(time_filter="day", limit=8),
        "hn": lambda: hackernews.fetch(hours_back=24),
        "arxiv": lambda: arxiv.fetch(days_back=1),
        "github": lambda: github_trending.fetch(since="daily"),
        "trends": lambda: google_trends.fetch(timeframe="now 1-d"),
        "producthunt": lambda: producthunt.fetch(),
    }

    print("📡 Scraping läuft parallel...")
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fn): name for name, fn in scrapers.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                data = future.result(timeout=60)
                results[name] = data
                print(f"  ✓ {name}: {len(data)} Einträge")
            except Exception as e:
                print(f"  ✗ {name}: Fehler – {e}")
                results[name] = []

    print("🧠 Claude generiert Briefing...")
    try:
        briefing = summarizer.generate_daily(
            reddit=results.get("reddit", []),
            hn=results.get("hn", []),
            arxiv=results.get("arxiv", []),
            github=results.get("github", []),
            trends=results.get("trends", []),
            producthunt=results.get("producthunt", []),
            date_str=date_str,
        )
    except Exception as e:
        print(f"✗ Claude Fehler: {e}")
        sys.exit(1)

    print("📤 Sende via Telegram...")
    try:
        success = telegram_sender.send(briefing)
        if success:
            print("✅ Daily Briefing erfolgreich gesendet!")
        else:
            print("⚠️  Telegram Fehler beim Senden")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Telegram Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
