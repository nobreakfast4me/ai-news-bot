"""Claude AI summarizer – compiles all scraped data into a briefing."""

import os
import json
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

DAILY_SYSTEM = """Du bist ein präziser KI-Nachrichtenredakteur. Du erhältst Rohdaten aus mehreren Quellen (Reddit, Hacker News, ArXiv, GitHub Trending, Google Trends, ProductHunt) und erstellst ein kompaktes, hochwertiges deutsches Daily Briefing über die heißesten KI-Entwicklungen der letzten 24 Stunden.

Formatierungsregeln:
- Nutze Telegram Markdown (fett: *text*, kursiv: _text_, Code: `code`)
- Maximal 3800 Zeichen gesamt
- Keine Emojis außer den vorgegebenen
- Jeder Punkt: 1-2 Sätze + Link
- Priorisiere: echte Neuigkeiten > virale Diskussionen > neue Tools > Paper"""

WEEKLY_SYSTEM = """Du bist ein präziser KI-Analyst. Du erhältst Rohdaten aus mehreren Quellen (Reddit, Hacker News, ArXiv, GitHub Trending, Google Trends, ProductHunt) und erstellst einen kompakten, hochwertigen deutschen Weekly Report über die wichtigsten KI-Trends der letzten 7 Tage.

Formatierungsregeln:
- Nutze Telegram Markdown (fett: *text*, kursiv: _text_, Code: `code`)
- Maximal 3800 Zeichen gesamt
- Keine Emojis außer den vorgegebenen
- Strukturiere nach Kategorien
- Priorisiere: Mega-Trends > Wichtige Releases > Top Tools > Forschung"""

DAILY_PROMPT_TEMPLATE = """Heute ist {date}. Hier sind die Rohdaten der letzten 24 Stunden:

## REDDIT (Top Posts):
{reddit_data}

## HACKER NEWS (Top AI Stories):
{hn_data}

## ARXIV (Neue KI-Paper):
{arxiv_data}

## GITHUB TRENDING (AI Repos heute):
{github_data}

## GOOGLE TRENDS (AI-Suchtrends):
{trends_data}

## PRODUCTHUNT (Neue AI-Tools):
{ph_data}

---

Erstelle jetzt das Daily Briefing in exakt diesem Format:

🔥 *AI Daily Briefing – {date}*

*🚀 TOP-NEWS DES TAGES*
[Die 3-4 wichtigsten Entwicklungen, jede mit 1-2 Sätzen + Link]

*⚡ VIRAL & HEISS DISKUTIERT*
[2-3 Themen die gerade auf Reddit/HN abgehen]

*🛠 NEUE AI-TOOLS & RELEASES*
[2-3 neue Tools/Produkte]

*📄 FORSCHUNG (ARXIV)*
[1-2 besonders relevante Paper]

*📈 TRENDS (GOOGLE)*
[Top 3-5 AI-Suchtrends als kommagetrennte Liste]

_Quellen: Reddit · HN · ArXiv · GitHub · Google Trends · ProductHunt_"""

WEEKLY_PROMPT_TEMPLATE = """Heute ist {date}. Hier sind die Rohdaten der letzten 7 Tage:

## REDDIT (Top Posts der Woche):
{reddit_data}

## HACKER NEWS (Top AI Stories der Woche):
{hn_data}

## ARXIV (KI-Paper der Woche):
{arxiv_data}

## GITHUB TRENDING (AI Repos diese Woche):
{github_data}

## GOOGLE TRENDS (AI-Suchtrends diese Woche):
{trends_data}

## PRODUCTHUNT (Neue AI-Tools):
{ph_data}

---

Erstelle jetzt den Weekly Report in exakt diesem Format:

📊 *AI Weekly Report – KW{week} ({date})*

*🔥 DIE MEGA-TRENDS DIESER WOCHE*
[Die 2-3 dominierenden Themen mit Kontext]

*🚀 WICHTIGSTE RELEASES & ANKÜNDIGUNGEN*
[3-4 bedeutende Releases, Tools oder Modelle]

*🛠 HEISSE NEUE AI-TOOLS*
[Top 3 neue Tools die man kennen muss]

*📄 FORSCHUNGS-HIGHLIGHTS*
[2-3 wichtige Paper/Durchbrüche]

*📈 SUCHTREND-ANALYSE*
[Welche AI-Begriffe diese Woche am meisten gesucht wurden + kurze Einschätzung warum]

*💡 TAKE-AWAYS: WAS MUSS MAN IMPLEMENTIEREN/WISSEN?*
[3-5 Bullet Points: konkrete Handlungsempfehlungen]

_Quellen: Reddit · HN · ArXiv · GitHub · Google Trends · ProductHunt_"""


def _format_list(items: list[dict], max_items: int = 10) -> str:
    if not items:
        return "(keine Daten verfügbar)"
    lines = []
    for item in items[:max_items]:
        source = item.get("source", "")
        if source == "Reddit":
            lines.append(
                f"- [{item.get('subreddit')}] {item.get('title')} "
                f"(↑{item.get('score', 0)}, 💬{item.get('comments', 0)}) "
                f"{item.get('url', '')}"
            )
        elif source == "Hacker News":
            lines.append(
                f"- {item.get('title')} "
                f"(↑{item.get('score', 0)}) "
                f"{item.get('url', '')}"
            )
        elif source == "ArXiv":
            lines.append(
                f"- {item.get('title')} [{item.get('category')}] "
                f"von {item.get('authors', '')} "
                f"| {item.get('abstract', '')[:200]} "
                f"{item.get('url', '')}"
            )
        elif source == "GitHub Trending":
            lines.append(
                f"- {item.get('name')}: {item.get('description', '')} "
                f"(⭐{item.get('stars', 0)}, {item.get('stars_period', '')}) "
                f"{item.get('url', '')}"
            )
        elif "Google Trends" in source:
            lines.append(
                f"- {item.get('keyword')} (Score: {item.get('interest_score', 0)})"
            )
        elif source == "ProductHunt":
            lines.append(
                f"- {item.get('title')}: {item.get('description', '')} "
                f"{item.get('url', '')}"
            )
        else:
            lines.append(f"- {json.dumps(item, ensure_ascii=False)[:200]}")
    return "\n".join(lines)


def generate_daily(
    reddit: list,
    hn: list,
    arxiv: list,
    github: list,
    trends: list,
    producthunt: list,
    date_str: str,
) -> str:
    prompt = DAILY_PROMPT_TEMPLATE.format(
        date=date_str,
        reddit_data=_format_list(reddit, 12),
        hn_data=_format_list(hn, 10),
        arxiv_data=_format_list(arxiv, 8),
        github_data=_format_list(github, 8),
        trends_data=_format_list(trends, 10),
        ph_data=_format_list(producthunt, 8),
    )

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        system=DAILY_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_weekly(
    reddit: list,
    hn: list,
    arxiv: list,
    github: list,
    trends: list,
    producthunt: list,
    date_str: str,
    week_number: int,
) -> str:
    prompt = WEEKLY_PROMPT_TEMPLATE.format(
        date=date_str,
        week=week_number,
        reddit_data=_format_list(reddit, 15),
        hn_data=_format_list(hn, 12),
        arxiv_data=_format_list(arxiv, 12),
        github_data=_format_list(github, 10),
        trends_data=_format_list(trends, 12),
        ph_data=_format_list(producthunt, 10),
    )

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2500,
        system=WEEKLY_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
