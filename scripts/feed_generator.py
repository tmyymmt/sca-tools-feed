import json
from datetime import datetime, timezone
from typing import List

from feedgen.feed import FeedGenerator

from scripts.models import ReleaseEntry


def _parse_dt(dt_str: str) -> datetime:
    """ISO 8601文字列をtzaware datetimeに変換する。"""
    return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))


def generate_rss(entries: List[ReleaseEntry], feed_title: str, feed_url: str) -> bytes:
    """RSS 2.0フィードを生成して返す。"""
    fg = FeedGenerator()
    fg.id(feed_url)
    fg.title(feed_title)
    fg.link(href=feed_url, rel="self")
    fg.description(f"{feed_title} - SCA tool release feed")
    fg.language("en")

    for entry in entries:
        fe = fg.add_entry()
        fe.id(entry.url)
        fe.title(f"[{entry.tool_name}] {entry.summary}")
        fe.link(href=entry.url)
        fe.description(entry.body or entry.summary)
        fe.pubDate(_parse_dt(entry.published_at))
        fe.category({"term": entry.category})

    return fg.rss_str(pretty=True)


def generate_atom(entries: List[ReleaseEntry], feed_title: str, feed_url: str) -> bytes:
    """Atom 1.0フィードを生成して返す。"""
    fg = FeedGenerator()
    fg.id(feed_url)
    fg.title(feed_title)
    fg.link(href=feed_url, rel="self")
    fg.description(f"{feed_title} - SCA tool release feed")
    fg.language("en")

    for entry in entries:
        fe = fg.add_entry()
        fe.id(entry.url)
        fe.title(f"[{entry.tool_name}] {entry.summary}")
        fe.link(href=entry.url)
        fe.content(entry.body or entry.summary, type="text")
        fe.published(_parse_dt(entry.published_at))
        fe.updated(_parse_dt(entry.published_at))
        fe.category({"term": entry.category})

    return fg.atom_str(pretty=True)


def generate_json_feed(entries: List[ReleaseEntry], feed_title: str, feed_url: str) -> str:
    """JSON Feed 1.1を生成して返す。"""
    items = []
    for entry in entries:
        items.append({
            "id": entry.url,
            "url": entry.url,
            "title": f"[{entry.tool_name}] {entry.summary}",
            "content_text": entry.body or entry.summary,
            "date_published": entry.published_at,
            "tags": [entry.category],
            "_tool_id": entry.tool_id,
            "_version": entry.version,
        })
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": feed_title,
        "feed_url": feed_url,
        "items": items,
    }
    return json.dumps(feed, ensure_ascii=False, indent=2)
