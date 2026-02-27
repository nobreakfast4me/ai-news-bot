# AI News Telegram Bot

Tägliches + wöchentliches KI-Briefing via Telegram — vollautomatisch in GitHub Actions, kein Server nötig.

**Quellen:** Reddit · Hacker News · ArXiv · GitHub Trending · Google Trends · ProductHunt
**KI-Analyse:** Claude Opus 4.6

---

## Einrichtung (einmalig, ~10 Minuten)

### 1. Repository auf GitHub erstellen

```bash
# Dieses Verzeichnis als neues GitHub Repo pushen
cd ai-news-bot
git init
git add .
git commit -m "Initial commit"
# Dann auf github.com ein neues Repo erstellen und pushen:
git remote add origin https://github.com/DEIN-USERNAME/ai-news-bot.git
git push -u origin main
```

### 2. Telegram Bot erstellen

1. Öffne Telegram → suche `@BotFather`
2. Schreibe `/newbot` → vergib einen Namen und Username
3. Du bekommst deinen **Bot Token** (z.B. `7123456789:AAF...`)
4. Schreibe deinem neuen Bot eine Nachricht (einmalig, damit der Bot dir schreiben darf)
5. Deine Chat-ID ermitteln: schreibe `@userinfobot` auf Telegram → gibt deine ID aus

### 3. Anthropic API Key

1. Gehe zu [console.anthropic.com](https://console.anthropic.com)
2. API Keys → Create Key
3. Key kopieren und sicher aufbewahren

### 5. GitHub Secrets einrichten

Im GitHub Repository: **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Wert |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Dein Bot Token von @BotFather |
| `TELEGRAM_CHAT_ID` | Deine Chat-ID von @userinfobot |
| `ANTHROPIC_API_KEY` | Dein Anthropic API Key |

### 6. Bot testen

Im GitHub Repository: **Actions → AI Daily Briefing → Run workflow**

Der Bot läuft, sammelt Daten und schickt dir das Briefing. Fertig!

---

## Automatischer Zeitplan

| Report | Wann | Cron |
|---|---|---|
| Daily Briefing | Täglich 08:00 MEZ | `0 7 * * *` |
| Weekly Report | Montags 08:00 MEZ | `0 7 * * 1` |

> GitHub Actions Cron-Jobs können bis zu 30 Minuten verspätet starten — für tägliche Reports kein Problem.

---

## Projektstruktur

```
ai-news-bot/
├── .github/workflows/
│   ├── daily-report.yml      # täglich
│   └── weekly-report.yml     # wöchentlich (montags)
├── src/
│   ├── scrapers/
│   │   ├── reddit.py         # Reddit Top Posts
│   │   ├── hackernews.py     # HN Algolia API
│   │   ├── arxiv.py          # ArXiv AI/ML Paper
│   │   ├── github_trending.py # GitHub Trending Repos
│   │   ├── google_trends.py  # Google Trends Keywords
│   │   └── producthunt.py    # ProductHunt AI Tools
│   ├── summarizer.py         # Claude Opus 4.6 Briefing
│   └── telegram_sender.py    # Telegram Bot API
├── daily.py                  # Entry Point täglicher Job
├── weekly.py                 # Entry Point wöchentlicher Job
└── requirements.txt
```

---

## Kosten (Schätzung)

| Posten | Kosten |
|---|---|
| GitHub Actions | Kostenlos (2000 min/Monat, reicht locker) |
| Claude Opus 4.6 | ~$0.05–0.15 pro Briefing |
| Reddit / HN / ArXiv / GitHub | Kostenlos |
| Google Trends (pytrends) | Kostenlos |

**Ca. $2–5/Monat** für die gesamte Nutzung.
