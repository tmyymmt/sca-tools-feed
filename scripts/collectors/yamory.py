import logging
import re
from datetime import datetime, timezone
from typing import List

import requests
from bs4 import BeautifulSoup

from scripts.categorize import classify_release
from scripts.models import ReleaseEntry

logger = logging.getLogger(__name__)
BASE_URL = "https://yamory.io"
NEWS_URL = f"{BASE_URL}/news"


def collect_yamory() -> List[ReleaseEntry]:
    """Yamoryお知らせページからリリース情報を収集する。

    エラー時は空リストを返す（部分失敗を許容）。
    """
    try:
        resp = requests.get(NEWS_URL, timeout=30)
        if not resp.ok:
            logger.warning("Yamory news returned status %d", resp.status_code)
            return []
    except requests.RequestException as e:
        logger.warning("Failed to fetch Yamory news: %s", e)
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    entries = []

    # h3タグ内のaリンクとその直後のh4/span要素から日付を取得
    for heading in soup.find_all(["h3", "h2"]):
        link = heading.find("a")
        if not link:
            continue
        title = link.get_text(strip=True)
        href = link.get("href", "")
        if not href:
            continue

        # 絶対URLに変換
        url = href if href.startswith("http") else f"{BASE_URL}{href}"

        # 日付を探す（直後のh4タグ、span.date など）
        date_text = ""
        next_el = heading.find_next(["h4", "span", "time"])
        if next_el:
            date_text = next_el.get_text(strip=True)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", date_text)
        if date_match:
            published_at = f"{date_match.group(1)}T00:00:00Z"
        else:
            # 日本語形式 "2026年3月31日" を試みる
            jp_date = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_text)
            if jp_date:
                published_at = (
                    f"{jp_date.group(1)}-{int(jp_date.group(2)):02d}"
                    f"-{int(jp_date.group(3)):02d}T00:00:00Z"
                )
            else:
                published_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        entry = ReleaseEntry(
            tool_id="yamory",
            tool_name="Yamory",
            version=date_text[:20] if date_match else title[:50],
            published_at=published_at,
            url=url,
            summary=title,
            body="",
            category=classify_release(title, "", "scrape_yamory"),
        )
        entries.append(entry)

    return entries
