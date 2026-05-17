import json
import os
import tempfile
from typing import List

from scripts.models import ReleaseEntry


def load_entries(path: str) -> List[ReleaseEntry]:
    """JSONファイルからエントリを読み込む。ファイルが存在しない場合は空リストを返す。"""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [ReleaseEntry.from_dict(d) for d in data]


def save_entries(path: str, entries: List[ReleaseEntry]) -> None:
    """エントリをJSONファイルにアトミックに書き込む（tempfile → os.replace）。"""
    dir_path = os.path.dirname(os.path.abspath(path))
    os.makedirs(dir_path, exist_ok=True)
    data = [e.to_dict() for e in entries]
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        os.unlink(tmp_path)
        raise


def merge_entries(existing: List[ReleaseEntry], new: List[ReleaseEntry]) -> List[ReleaseEntry]:
    """新しいエントリを既存エントリにマージする（URLで重複排除、新しいものを先頭に）。

    既存エントリの body が空で新エントリに body がある場合は既存エントリを更新する。
    """
    existing_by_url = {e.url: e for e in existing}
    # body が空の既存エントリを新しいエントリで上書き
    for e in new:
        if e.url in existing_by_url and not existing_by_url[e.url].body and e.body:
            existing_by_url[e.url] = e
    truly_new = [e for e in new if e.url not in existing_by_url]
    updated_existing = [existing_by_url[e.url] for e in existing]
    return truly_new + updated_existing
