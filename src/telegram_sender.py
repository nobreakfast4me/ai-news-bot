"""Telegram sender – sends messages via Bot API."""

import os
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"
MAX_LENGTH = 4096


def send(text: str) -> bool:
    """Send a message to the configured Telegram chat. Splits if > 4096 chars."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set.")

    # Split message if too long
    chunks = _split_message(text)

    success = True
    for chunk in chunks:
        url = TELEGRAM_API.format(token=token, method="sendMessage")
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if not result.get("ok"):
                # Fallback: try without markdown parsing
                payload["parse_mode"] = "HTML"
                payload["text"] = _escape_html(chunk)
                resp2 = requests.post(url, json=payload, timeout=30)
                if not resp2.json().get("ok"):
                    print(f"[Telegram] Failed to send chunk: {result}")
                    success = False
        except requests.RequestException as e:
            print(f"[Telegram] Request error: {e}")
            success = False

    return success


def _split_message(text: str) -> list[str]:
    """Split text into chunks of max MAX_LENGTH characters at newlines."""
    if len(text) <= MAX_LENGTH:
        return [text]

    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > MAX_LENGTH:
            if current:
                chunks.append(current.rstrip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        chunks.append(current.rstrip())
    return chunks


def _escape_html(text: str) -> str:
    """Basic HTML escaping as fallback."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
