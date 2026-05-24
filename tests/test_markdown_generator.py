"""tests/test_markdown_generator.py"""
import pytest

from scripts.markdown_generator import (
    generate_comparison_page,
    generate_comparison_page_ja,
    generate_tool_page,
    generate_tool_page_ja,
    render_html,
)
from scripts.models import ReleaseEntry

TOOL = {
    "id": "trivy",
    "name": "Trivy",
    "type": "github",
    "repo": "aquasecurity/trivy",
    "homepage": "https://trivy.dev",
    "license": "Apache-2.0",
    "pricing": "Free",
    "description": "Comprehensive vulnerability scanner.",
    "description_ja": "包括的な脆弱性スキャナー。",
    "features": {
        "container": True,
        "language_libs": True,
        "sbom": True,
        "policy": True,
        "saas": False,
    },
}

PAID_TOOL = {
    **TOOL,
    "id": "futurevuls",
    "name": "FutureVuls",
    "pricing": "Paid",
    "pricing_url": "https://www.vuls.biz/price",
}

ENTRIES = [
    ReleaseEntry(
        tool_id="trivy",
        tool_name="Trivy",
        version="v0.50.0",
        published_at="2024-03-01T00:00:00Z",
        url="https://github.com/aquasecurity/trivy/releases/tag/v0.50.0",
        summary="Trivy v0.50.0 released",
        body="## What's New\n- New feature A",
        category="feature",
    ),
    ReleaseEntry(
        tool_id="trivy",
        tool_name="Trivy",
        version="v0.49.0",
        published_at="2024-02-01T00:00:00Z",
        url="https://github.com/aquasecurity/trivy/releases/tag/v0.49.0",
        summary="Trivy v0.49.0 released",
        body="## Bug Fixes\n- Fixed issue B",
        category="bugfix",
    ),
]


def test_generate_tool_page_contains_latest_version():
    result = generate_tool_page(TOOL, ENTRIES)
    assert "v0.50.0" in result


def test_generate_tool_page_contains_all_versions():
    result = generate_tool_page(TOOL, ENTRIES)
    assert "v0.50.0" in result
    assert "v0.49.0" in result


def test_generate_tool_page_contains_category():
    result = generate_tool_page(TOOL, ENTRIES)
    assert "`feature`" in result
    assert "`bugfix`" in result


def test_generate_tool_page_empty_entries():
    result = generate_tool_page(TOOL, [])
    assert "No release data available." in result
    assert "—" in result  # latest version shows —


def test_generate_tool_page_contains_features():
    result = generate_tool_page(TOOL, ENTRIES)
    assert "✅" in result
    assert "Apache-2.0" in result
    assert "Free" in result


def test_generate_tool_page_links_paid_pricing():
    result = generate_tool_page(PAID_TOOL, ENTRIES)
    assert "[Paid](https://www.vuls.biz/price)" in result


def test_generate_tool_page_ja_contains_japanese_headers():
    result = generate_tool_page_ja(TOOL, ENTRIES)
    assert "基本情報" in result
    assert "リリース履歴" in result
    assert "機能" in result
    assert "v0.50.0" in result


def test_generate_tool_page_ja_uses_description_ja():
    result = generate_tool_page_ja(TOOL, ENTRIES)
    assert "包括的な脆弱性スキャナー" in result


def test_generate_comparison_page_contains_all_tools():
    tools = [TOOL, {**TOOL, "id": "grype", "name": "Grype"}]
    entries_by_tool = {"trivy": ENTRIES, "grype": []}
    result = generate_comparison_page(tools, entries_by_tool)
    assert "Trivy" in result
    assert "Grype" in result
    assert "v0.50.0" in result


def test_generate_comparison_page_ja_contains_japanese_header():
    tools = [TOOL]
    result = generate_comparison_page_ja(tools, {"trivy": ENTRIES})
    assert "SCAツール比較" in result
    assert "概要版" in result


def test_generate_comparison_page_empty_entries_shows_dash():
    tools = [TOOL]
    result = generate_comparison_page(tools, {"trivy": []})
    assert "—" in result


def test_generate_comparison_page_links_to_html():
    tools = [TOOL]
    result = generate_comparison_page(tools, {"trivy": ENTRIES})
    assert "trivy.html" in result
    assert ".md" not in result


def test_generate_comparison_page_links_paid_pricing():
    tools = [PAID_TOOL]
    result = generate_comparison_page(tools, {"futurevuls": ENTRIES})
    assert "[Paid](https://www.vuls.biz/price)" in result


def test_generate_comparison_page_ja_links_to_html():
    tools = [TOOL]
    result = generate_comparison_page_ja(tools, {"trivy": ENTRIES})
    assert "trivy_ja.html" in result
    assert ".md" not in result


def test_render_html_returns_html_document():
    result = render_html("Test Title", "# Hello\n\nWorld")
    assert "<!DOCTYPE html>" in result
    assert "<title>Test Title</title>" in result
    assert "<h1>Hello</h1>" in result


def test_render_html_lang_ja():
    result = render_html("テスト", "# こんにちは", lang="ja")
    assert 'lang="ja"' in result


def test_render_html_renders_table():
    md = "| A | B |\n|---|---|\n| 1 | 2 |"
    result = render_html("T", md)
    assert "<table>" in result


def test_render_html_contains_dark_mode():
    result = render_html("T", "# Hello")
    assert "prefers-color-scheme: dark" in result
