import pytest
from scripts.storage import load_entries, save_entries, merge_entries
from scripts.models import ReleaseEntry


def make_entry(tool_id="trivy", url="https://example.com/v1.0", version="v1.0"):
    return ReleaseEntry(
        tool_id=tool_id,
        tool_name="Trivy",
        version=version,
        published_at="2024-01-15T10:00:00Z",
        url=url,
        summary=f"Trivy {version}",
        body="## Changes\n- fix: something",
        category="feature",
    )


def test_save_and_load_entries(tmp_path):
    entries = [make_entry()]
    path = tmp_path / "trivy.json"
    save_entries(str(path), entries)
    loaded = load_entries(str(path))
    assert len(loaded) == 1
    assert loaded[0].url == "https://example.com/v1.0"
    assert loaded[0].tool_id == "trivy"


def test_load_entries_returns_empty_list_when_file_missing(tmp_path):
    path = tmp_path / "nonexistent.json"
    result = load_entries(str(path))
    assert result == []


def test_merge_entries_deduplicates_by_url():
    existing = [make_entry(url="https://example.com/v1.0", version="v1.0")]
    new = [
        make_entry(url="https://example.com/v1.0", version="v1.0"),  # duplicate
        make_entry(url="https://example.com/v2.0", version="v2.0"),  # new
    ]
    merged = merge_entries(existing, new)
    assert len(merged) == 2
    urls = [e.url for e in merged]
    assert "https://example.com/v2.0" in urls
    assert urls.count("https://example.com/v1.0") == 1


def test_merge_entries_prepends_new_entries():
    existing = [make_entry(url="https://example.com/v1.0", version="v1.0")]
    new = [make_entry(url="https://example.com/v2.0", version="v2.0")]
    merged = merge_entries(existing, new)
    assert merged[0].url == "https://example.com/v2.0"


def test_save_entries_is_atomic(tmp_path):
    """アトミック書き込み: 一時ファイルが残らないことを確認する。"""
    entries = [make_entry()]
    path = tmp_path / "trivy.json"
    save_entries(str(path), entries)
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert tmp_files == []
