import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import List

from bs4 import BeautifulSoup

from scripts.categorize import classify_release
from scripts.models import ReleaseEntry

logger = logging.getLogger(__name__)
BASE_URL = "https://yamory.io"
NEWS_URL = f"{BASE_URL}/news"


async def _fetch_yamory_html() -> str:
    """Playwright を使って JS レンダリング後の HTML を取得する。"""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto(NEWS_URL, wait_until="networkidle", timeout=30000)
            return await page.content()
        finally:
            await browser.close()


def collect_yamory() -> List[ReleaseEntry]:
    """Yamoryお知らせページからリリース情報を収集する。

    エラー時は空リストを返す（部分失敗を許容）。
    """
    try:
        html = asyncio.run(_fetch_yamory_html())
    except Exception as e:
        logger.warning("Failed to fetch Yamory news via Playwright: %s", e)
        return []

    soup = BeautifulSoup(html, "html.parser")
    entries = []

    # 構造: div.cont > h3 > a (タイトル+リンク), div.cont > h4 (日付 YYYY-MM-DD)
    for heading in soup.find_all("h3"):
        link = heading.find("a")
        if not link:
            continue
        title = link.get_text(strip=True)
        href = link.get("href", "")
        if not href:
            continue

        # 絶対URLに変換
        url = href if href.startswith("http") else f"{BASE_URL}{href}"

        # 同じ親要素内の h4 から日付を取得
        date_text = ""
        parent = heading.parent
        if parent:
            h4 = parent.find("h4")
            if h4:
                date_text = h4.get_text(strip=True)

        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", date_text)
        if date_match:
            published_at = f"{date_match.group(1)}T00:00:00Z"
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
