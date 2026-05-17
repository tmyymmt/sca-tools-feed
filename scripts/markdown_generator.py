"""ツールごとのまとめページおよび比較ページをMarkdownで生成する。"""
from datetime import datetime, timezone
from typing import Dict, List, Optional

from scripts.models import ReleaseEntry

BOOL_MARK: Dict[bool, str] = {True: "✅", False: "❌"}


def _latest_entry(entries: List[ReleaseEntry]) -> Optional[ReleaseEntry]:
    return entries[0] if entries else None


def _homepage(tool: dict) -> str:
    hp = tool.get("homepage", tool.get("url", ""))
    if hp:
        return hp
    repo = tool.get("repo", "")
    return f"https://github.com/{repo}" if repo else "—"


def _tool_type(tool: dict) -> str:
    return "SaaS" if tool.get("features", {}).get("saas") else "OSS"


def _feature_mark(tool: dict, key: str) -> str:
    return BOOL_MARK.get(tool.get("features", {}).get(key, False), "—")


def generate_tool_page(tool: dict, entries: List[ReleaseEntry]) -> str:
    """ツールごとのまとめページ（英語）を生成する。"""
    name = tool["name"]
    latest = _latest_entry(entries)
    latest_version = latest.version if latest else "—"
    last_updated = latest.published_at[:10] if latest else "—"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# {name}",
        "",
        f"> {tool.get('description', '')}",
        "",
        "## Overview",
        "",
        "| Item | Value |",
        "|------|-------|",
        f"| Type | {_tool_type(tool)} |",
        f"| License | {tool.get('license', '—')} |",
        f"| Pricing | {tool.get('pricing', '—')} |",
        f"| Homepage | {_homepage(tool)} |",
        f"| Latest Version | {latest_version} |",
        f"| Last Updated | {last_updated} |",
        "",
        "## Features",
        "",
        "| Feature | Supported |",
        "|---------|-----------|",
        f"| Container Scanning | {_feature_mark(tool, 'container')} |",
        f"| Language/Library Scanning | {_feature_mark(tool, 'language_libs')} |",
        f"| SBOM Generation | {_feature_mark(tool, 'sbom')} |",
        f"| Policy Evaluation | {_feature_mark(tool, 'policy')} |",
        "",
        "## Release History",
        "",
    ]

    if not entries:
        lines.append("*No release data available.*")
        lines.append("")
    else:
        for entry in entries:
            date = entry.published_at[:10]
            lines.append(f"### {entry.version} — {date} `{entry.category}`")
            lines.append("")
            if entry.summary:
                lines.append(entry.summary)
                lines.append("")
            if entry.body and entry.body.strip():
                lines.append(entry.body.strip())
                lines.append("")
            lines.append("---")
            lines.append("")

    lines.append(f"*Generated at {now}*")
    lines.append("")

    return "\n".join(lines)


def generate_tool_page_ja(tool: dict, entries: List[ReleaseEntry]) -> str:
    """ツールごとのまとめページ（日本語）を生成する。"""
    name = tool["name"]
    latest = _latest_entry(entries)
    latest_version = latest.version if latest else "—"
    last_updated = latest.published_at[:10] if latest else "—"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    description = tool.get("description_ja", tool.get("description", ""))

    lines = [
        f"# {name}",
        "",
        f"> {description}",
        "",
        "## 基本情報",
        "",
        "| 項目 | 内容 |",
        "|------|------|",
        f"| 種別 | {_tool_type(tool)} |",
        f"| ライセンス | {tool.get('license', '—')} |",
        f"| 費用 | {tool.get('pricing', '—')} |",
        f"| 公式サイト | {_homepage(tool)} |",
        f"| 最新バージョン | {latest_version} |",
        f"| 最終更新日 | {last_updated} |",
        "",
        "## 機能",
        "",
        "| 機能 | 対応 |",
        "|------|------|",
        f"| コンテナスキャン | {_feature_mark(tool, 'container')} |",
        f"| 言語/ライブラリスキャン | {_feature_mark(tool, 'language_libs')} |",
        f"| SBOM生成 | {_feature_mark(tool, 'sbom')} |",
        f"| ポリシー評価 | {_feature_mark(tool, 'policy')} |",
        "",
        "## リリース履歴",
        "",
    ]

    if not entries:
        lines.append("*リリースデータがありません。*")
        lines.append("")
    else:
        for entry in entries:
            date = entry.published_at[:10]
            lines.append(f"### {entry.version} — {date} `{entry.category}`")
            lines.append("")
            if entry.summary:
                lines.append(entry.summary)
                lines.append("")
            if entry.body and entry.body.strip():
                lines.append(entry.body.strip())
                lines.append("")
            lines.append("---")
            lines.append("")

    lines.append(f"*{now} 時点の情報*")
    lines.append("")

    return "\n".join(lines)


def generate_comparison_page(tools: list, entries_by_tool: Dict[str, List[ReleaseEntry]]) -> str:
    """全ツール比較ページ（英語）を生成する。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# SCA Tools Comparison",
        "",
        f"*Generated at {now}*",
        "",
        "| Tool | Latest | Updated | Type | License | Pricing | Container | Lang/Lib | SBOM | Policy |",
        "|------|--------|---------|------|---------|---------|-----------|----------|------|--------|",
    ]

    for tool in tools:
        tid = tool["id"]
        latest = _latest_entry(entries_by_tool.get(tid, []))
        version = latest.version if latest else "—"
        updated = latest.published_at[:10] if latest else "—"
        lines.append(
            f"| [{tool['name']}]({tid}.md)"
            f" | {version}"
            f" | {updated}"
            f" | {_tool_type(tool)}"
            f" | {tool.get('license', '—')}"
            f" | {tool.get('pricing', '—')}"
            f" | {_feature_mark(tool, 'container')}"
            f" | {_feature_mark(tool, 'language_libs')}"
            f" | {_feature_mark(tool, 'sbom')}"
            f" | {_feature_mark(tool, 'policy')} |"
        )

    lines.append("")
    return "\n".join(lines)


def generate_comparison_page_ja(tools: list, entries_by_tool: Dict[str, List[ReleaseEntry]]) -> str:
    """全ツール比較ページ（日本語）を生成する。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# SCAツール比較",
        "",
        f"*{now} 時点の情報*",
        "",
        "## 比較表",
        "",
        "| ツール | 最新版 | 更新日 | 種別 | ライセンス | 費用 | コンテナ | 言語/ライブラリ | SBOM | ポリシー |",
        "|--------|--------|--------|------|-----------|------|---------|---------------|------|---------|",
    ]

    for tool in tools:
        tid = tool["id"]
        latest = _latest_entry(entries_by_tool.get(tid, []))
        version = latest.version if latest else "—"
        updated = latest.published_at[:10] if latest else "—"
        lines.append(
            f"| [{tool['name']}]({tid}_ja.md)"
            f" | {version}"
            f" | {updated}"
            f" | {_tool_type(tool)}"
            f" | {tool.get('license', '—')}"
            f" | {tool.get('pricing', '—')}"
            f" | {_feature_mark(tool, 'container')}"
            f" | {_feature_mark(tool, 'language_libs')}"
            f" | {_feature_mark(tool, 'sbom')}"
            f" | {_feature_mark(tool, 'policy')} |"
        )

    lines.append("")
    return "\n".join(lines)
