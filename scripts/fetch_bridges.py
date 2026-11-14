#!/usr/bin/env python3
"""Збирає повідомлення про мости/греблю з публічних Telegram-каналів (t.me/s/...)
і зберігає їх у bridges.json поруч з index.html. Лише стандартна бібліотека Python.

Запускається GitHub Actions кожні ~5 хвилин (.github/workflows/bridges.yml).
Нові повідомлення додаються до вже збережених, старші за 3 доби видаляються.
"""
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

CHANNELS = ["patrolpolicezp", "zoda_gov_ua"]
OUT = Path(__file__).resolve().parent.parent / "bridges.json"
KEEP_DAYS = 3

L = "а-яіїєґё"
RELEVANT = re.compile(
    rf"(^|[^{L}])(міст(?![{L}])|мост)|гребл|дніпрог[еe][сc]|днепрогэс|переправ|"
    r"перекри|обмежен|відновлено|відновили", re.I)

MSG_TEXT = re.compile(r'<div class="tgme_widget_message_text js-message_text[^"]*"[^>]*>(.*?)</div>', re.S)
REPLY_TEXT = re.compile(r'<div class="tgme_widget_message_text js-message_reply_text[^"]*"[^>]*>(.*?)</div>', re.S)
POST = re.compile(r'data-post="([^"]+)"')
TIME = re.compile(r'<time[^>]*datetime="([^"]+)"')


def to_text(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return html.unescape(fragment).strip()


def fetch(channel: str) -> list[dict]:
    req = urllib.request.Request(
        f"https://t.me/s/{channel}",
        headers={"User-Agent": "Mozilla/5.0 (bridges dashboard)", "Accept-Language": "uk,ru;q=0.8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        page = r.read().decode("utf-8", "replace")
    posts = []
    for wrap in page.split('<div class="tgme_widget_message_wrap')[1:]:
        p, tm, tx = POST.search(wrap), TIME.search(wrap), MSG_TEXT.search(wrap)
        if not (p and tm and tx):
            continue
        rp = REPLY_TEXT.search(wrap)
        posts.append({"ch": channel, "post": p.group(1), "time": tm.group(1),
                      "text": to_text(tx.group(1)), "reply": to_text(rp.group(1)) if rp else ""})
    return posts


def main() -> int:
    old = {}
    if OUT.exists():
        try:
            old = {p["post"]: p for p in json.loads(OUT.read_text("utf-8")).get("posts", [])}
        except Exception:
            old = {}
    merged = dict(old)
    ok = 0
    for ch in CHANNELS:
        try:
            for p in fetch(ch):
                if RELEVANT.search(p["text"]) or (p["reply"] and RELEVANT.search(p["reply"])):
                    merged[p["post"]] = p   # свіжа версія (повідомлення могли відредагувати)
            ok += 1
        except Exception as e:
            print(f"warning: {ch}: {e}", file=sys.stderr)
    if not ok:
        print("no channel fetched, keeping old file", file=sys.stderr)
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)
    posts = sorted((p for p in merged.values() if datetime.fromisoformat(p["time"]) >= cutoff),
                   key=lambda p: p["time"], reverse=True)
    if old and list(old) and posts == sorted(old.values(), key=lambda p: p["time"], reverse=True):
        print("no changes")
        return 0
    OUT.write_text(json.dumps({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                               "posts": posts}, ensure_ascii=False, indent=1), "utf-8")
    print(f"saved {len(posts)} posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
