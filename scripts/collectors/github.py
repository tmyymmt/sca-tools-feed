import logging
from typing import List, Optional

import requests

from scripts.categorize import classify_release
from scripts.models import ReleaseEntry

logger = logging.getLogger(__name__)


def collect_github_releases(
    tool_id: str,
    tool_name: str,
    repo: str,
    github_token: Optional[str] = None,
) -> List[ReleaseEntry]:
    """GitHub Releases APIからリリース情報を収集する。

    エラー時は空リストを返す（部分失敗を許容）。
    """
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return []

    if resp.status_code == 429:
        logger.warning("Rate limited for %s, skipping this run", repo)
        return []

    if resp.status_code == 404:
        logger.warning("Repository not found: %s", repo)
        return []

    if not resp.ok:
        logger.warning("Unexpected status %d for %s", resp.status_code, repo)
        return []

    releases = resp.json()
    entries = []
    for r in releases:
        title = r.get("name") or r.get("tag_name", "")
        body = r.get("body") or ""
        entry = ReleaseEntry(
            tool_id=tool_id,
            tool_name=tool_name,
            version=r["tag_name"],
            published_at=r["published_at"],
            url=r["html_url"],
            summary=title,
            body=body,
            category=classify_release(title, body, "github"),
        )
        entries.append(entry)
    return entries
