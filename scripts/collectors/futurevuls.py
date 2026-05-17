import logging
import re
from datetime import datetime, timezone
from typing import List

import requests
from bs4 import BeautifulSoup

from scripts.categorize import classify_release
from scripts.models import ReleaseEntry

logger = logging.getLogger(__name__)
BASE_URL = "https://help.vuls.biz"
INDEX_URL = f"{BASE_URL}/releasenotes/"


def collect_futurevuls() -> List[ReleaseEntry]:
    """FutureVulsリリースノート一覧ページからリリース情報を収集する。

    エラー時は空リストを返す（部分失敗を許容）。
    """
    try:
        resp = requests.get(INDEX_URL, timeout=30)
        if not resp.ok:
            logger.warning("FutureVuls index returned status %d", resp.status_code)
            return []
    except requests.RequestException as e:
        logger.warning("Failed to fetch FutureVuls index: %s", e)
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    entries = []

    for link in soup.find_all("a", href=re.compile(r"^/releasenotes/\d")):
        href = link.get("href", "")
        url = f"{BASE_URL}{href}"
        title = link.get_text(strip=True)

        # タイトルから日付を抽出: "2026-02-24" 形式
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", title)
        if date_match:
            published_at = f"{date_match.group(1)}T00:00:00Z"
        else:
            # "2026-01" のような年月のみの場合
            month_match = re.search(r"(\d{4})-(\d{2})", title)
            if month_match:
                published_at = f"{month_match.group(1)}-{month_match.group(2)}-01T00:00:00Z"
            else:
                published_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # hrefから日付を補完する（title に日付がない場合）
        if "T00:00:00Z" not in published_at:
            href_date = re.search(r"/(\d{4})(\d{2})(\d{2})", href)
            if href_date:
                published_at = f"{href_date.group(1)}-{href_date.group(2)}-{href_date.group(3)}T00:00:00Z"

        entry = ReleaseEntry(
            tool_id="futurevuls",
            tool_name="FutureVuls",
            version=title,
            published_at=published_at,
            url=url,
            summary=title,
            body="",
            category=classify_release(title, href, "scrape_futurevuls"),
        )
        entries.append(entry)

    return entries
