#!/usr/bin/env python3
"""Weekly AI News Bot – sammelt Daten der letzten 7 Tage und schickt Report via Telegram."""

import sys
import os
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.scrapers import reddit, hackernews, arxiv, github_trending, google_trends, producthunt
from src import summarizer, telegram_sender


def run():
    print("🤖 AI Weekly Report Bot gestartet...")
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%d.%m.%Y")
    week_number = now.isocalendar()[1]

    # Run all scrapers in parallel with weekly parameters
    results = {}
    scrapers = {
        "reddit": lambda: reddit.fetch(time_filter="week", limit=10),
        "hn": lambda: hackernews.fetch(hours_back=168),  # 7 days
        "arxiv": lambda: arxiv.fetch(days_back=7),
        "github": lambda: github_trending.fetch(since="weekly"),
        "trends": lambda: google_trends.fetch(timeframe="now 7-d"),
        "producthunt": lambda: producthunt.fetch(),
    }

    print("📡 Scraping läuft parallel...")
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fn): name for name, fn in scrapers.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                data = future.result(timeout=90)
                results[name] = data
                print(f"  ✓ {name}: {len(data)} Einträge")
            except Exception as e:
                print(f"  ✗ {name}: Fehler – {e}")
                results[name] = []

    print("🧠 Claude generiert Weekly Report...")
    try:
        report = summarizer.generate_weekly(
            reddit=results.get("reddit", []),
            hn=results.get("hn", []),
            arxiv=results.get("arxiv", []),
            github=results.get("github", []),
            trends=results.get("trends", []),
            producthunt=results.get("producthunt", []),
            date_str=date_str,
            week_number=week_number,
        )
    except Exception as e:
        print(f"✗ Claude Fehler: {e}")
        sys.exit(1)

    print("📤 Sende via Telegram...")
    try:
        success = telegram_sender.send(report)
        if success:
            print(f"✅ Weekly Report KW{week_number} erfolgreich gesendet!")
        else:
            print("⚠️  Telegram Fehler beim Senden")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Telegram Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
