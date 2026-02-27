# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

Automated Telegram bot that sends daily and weekly AI news briefings. Runs entirely in GitHub Actions (no server needed). Scrapes Reddit, Hacker News, ArXiv, GitHub Trending, Google Trends, and ProductHunt — then uses Claude Opus 4.6 to generate a formatted German-language briefing sent via Telegram Bot API.

## Running the bot locally

```bash
pip install -r requirements.txt

# Set required env vars first (see below), then:
python daily.py    # test daily briefing
python weekly.py   # test weekly briefing
```

Required environment variables:
- `ANTHROPIC_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Reddit uses the public JSON API — no credentials needed.

## Architecture

Two entry points (`daily.py`, `weekly.py`) that:
1. Run all scrapers in parallel via `ThreadPoolExecutor`
2. Pass aggregated results to `src/summarizer.py` (Claude Opus 4.6)
3. Send the formatted briefing via `src/telegram_sender.py`

**Scrapers** (`src/scrapers/`): Each returns `list[dict]` with a `source` field. They are independent and fail silently — one failing scraper never breaks the run.

**Summarizer** (`src/summarizer.py`): Takes lists from all scrapers, formats them as plain text, sends to Claude. Uses separate system prompts and templates for daily vs weekly. Output is Telegram Markdown.

**Telegram sender** (`src/telegram_sender.py`): Sends via Bot API with `parse_mode=Markdown`. Auto-splits messages exceeding 4096 chars.

## Deployment

GitHub Actions workflows in `.github/workflows/`:
- `daily-report.yml` — runs at `0 7 * * *` (08:00 MEZ)
- `weekly-report.yml` — runs at `0 7 * * 1` (Mondays 08:00 MEZ)

Both support `workflow_dispatch` for manual testing. Required GitHub Secrets: `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

## Key conventions

- All user-facing output (Telegram messages) is in **German**
- Scrapers must never raise exceptions to the caller — use `try/except` and return `[]`
- Claude model: always `claude-opus-4-6`
- Telegram message limit: 4096 chars — `telegram_sender.py` handles splitting
