#!/usr/bin/env python3
"""SCAツールのリリース情報を収集してフィードを生成するメインスクリプト。"""
import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, List

import yaml

from scripts.collectors.futurevuls import collect_futurevuls
from scripts.collectors.github import collect_github_releases
from scripts.collectors.yamory import collect_yamory
from scripts.feed_generator import generate_atom, generate_json_feed, generate_rss
from scripts.markdown_generator import (
    generate_comparison_page,
    generate_comparison_page_ja,
    generate_tool_page,
    generate_tool_page_ja,
)
from scripts.models import ReleaseEntry
from scripts.storage import load_entries, merge_entries, save_entries

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
FEEDS_DIR = Path("feeds")
PAGES_DIR = Path("pages")
TOOLS_CONFIG = Path("tools/tools.yml")
FEED_TITLE = "SCA Tools Feed"
FEED_BASE_URL = os.environ.get("FEED_BASE_URL", "https://tmyymmt.github.io/sca-tools-feed/feeds")


def load_tools_config() -> list:
    with open(TOOLS_CONFIG, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["tools"]


def collect_tool(tool: dict, github_token: str) -> List[ReleaseEntry]:
    """ツール設定に応じたコレクターを呼び出す。エラー時は空リストを返す。"""
    tool_type = tool["type"]
    try:
        if tool_type == "github":
            return collect_github_releases(
                tool_id=tool["id"],
                tool_name=tool["name"],
                repo=tool["repo"],
                github_token=github_token,
            )
        elif tool_type == "scrape_futurevuls":
            return collect_futurevuls()
        elif tool_type == "scrape_yamory":
            return collect_yamory()
        else:
            logger.warning("Unknown tool type: %s", tool_type)
            return []
    except Exception as e:
        logger.error("Unexpected error collecting %s: %s", tool["id"], e)
        return []


def write_file_atomic(path: Path, content: bytes) -> None:
    """バイト列をファイルにアトミックに書き込む。"""
    dir_path = path.parent
    dir_path.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(dir_path), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        os.unlink(tmp)
        raise


def write_feeds(all_entries: List[ReleaseEntry]) -> None:
    """全エントリおよびツール別のRSS/Atom/JSON Feedをアトミックに書き込む。"""
    FEEDS_DIR.mkdir(exist_ok=True)
    base_url = FEED_BASE_URL

    # 全ツール統合フィード
    write_file_atomic(FEEDS_DIR / "all.rss", generate_rss(all_entries, FEED_TITLE, f"{base_url}/all.rss"))
    write_file_atomic(FEEDS_DIR / "all.atom", generate_atom(all_entries, FEED_TITLE, f"{base_url}/all.atom"))
    write_file_atomic(
        FEEDS_DIR / "all.json",
        generate_json_feed(all_entries, FEED_TITLE, f"{base_url}/all.json").encode("utf-8"),
    )

    # ツール別フィード
    tool_ids = dict.fromkeys(e.tool_id for e in all_entries)  # 順序を保持
    for tool_id in tool_ids:
        tool_entries = [e for e in all_entries if e.tool_id == tool_id]
        tool_name = tool_entries[0].tool_name if tool_entries else tool_id
        title = f"{FEED_TITLE} - {tool_name}"
        write_file_atomic(FEEDS_DIR / f"{tool_id}.rss", generate_rss(tool_entries, title, f"{base_url}/{tool_id}.rss"))
        write_file_atomic(FEEDS_DIR / f"{tool_id}.atom", generate_atom(tool_entries, title, f"{base_url}/{tool_id}.atom"))
        write_file_atomic(
            FEEDS_DIR / f"{tool_id}.json",
            generate_json_feed(tool_entries, title, f"{base_url}/{tool_id}.json").encode("utf-8"),
        )

    logger.info("Feeds written to %s/", FEEDS_DIR)


def write_pages(tools: list, entries_by_tool: Dict[str, List[ReleaseEntry]]) -> None:
    """ツールごとのまとめページと比較ページをMarkdownで書き込む。"""
    PAGES_DIR.mkdir(exist_ok=True)

    for tool in tools:
        tid = tool["id"]
        tool_entries = entries_by_tool.get(tid, [])
        write_file_atomic(
            PAGES_DIR / f"{tid}.md",
            generate_tool_page(tool, tool_entries).encode("utf-8"),
        )
        write_file_atomic(
            PAGES_DIR / f"{tid}_ja.md",
            generate_tool_page_ja(tool, tool_entries).encode("utf-8"),
        )

    write_file_atomic(
        PAGES_DIR / "comparison.md",
        generate_comparison_page(tools, entries_by_tool).encode("utf-8"),
    )
    write_file_atomic(
        PAGES_DIR / "comparison_ja.md",
        generate_comparison_page_ja(tools, entries_by_tool).encode("utf-8"),
    )
    logger.info("Pages written to %s/", PAGES_DIR)


def main() -> None:
    github_token = os.environ.get("GITHUB_TOKEN")
    tools = load_tools_config()
    DATA_DIR.mkdir(exist_ok=True)

    all_entries: List[ReleaseEntry] = []
    entries_by_tool: Dict[str, List[ReleaseEntry]] = {}
    failed_tools = []

    for tool in tools:
        logger.info("Collecting %s (%s)...", tool["name"], tool["type"])
        new_entries = collect_tool(tool, github_token)

        if not new_entries:
            logger.warning("No entries collected for %s", tool["id"])
            failed_tools.append(tool["id"])

        data_path = str(DATA_DIR / f"{tool['id']}.json")
        existing = load_entries(data_path)
        merged = merge_entries(existing, new_entries)
        if len(merged) != len(existing):
            save_entries(data_path, merged)
            logger.info("Saved %d entries for %s (+%d new)", len(merged), tool["id"], len(merged) - len(existing))

        entries_by_tool[tool["id"]] = merged
        all_entries.extend(merged)

    # 公開日時でソート（新しい順）
    all_entries.sort(key=lambda e: e.published_at, reverse=True)

    write_feeds(all_entries)
    write_pages(tools, entries_by_tool)

    if failed_tools:
        logger.warning("Failed to collect from: %s", ", ".join(failed_tools))

    logger.info("Done.")


if __name__ == "__main__":
    main()
