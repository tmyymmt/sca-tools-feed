# sca-tools-feed Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Mark each checkbox completed immediately after finishing.

**Goal:** SCAツール（Trivy, Grype, Syft等）のリリース情報をGitHub Releases APIおよびHTMLスクレイピングで収集し、RSS 2.0 / Atom 1.0 / JSON Feed 1.1として生成・GitHub Pagesで公開するシステムを構築する。

**Architecture overview:**
- Pythonスクリプトで各ツールのリリース情報を収集 → `data/{tool_id}.json`（中間形式）に永続化
- `data/` の全JSONを読み込んでRSS/Atom/JSON Feedを生成 → `feeds/` ディレクトリに出力
- GitHub Actionsで日次実行、mainブランチにコミット、GitHub Pagesで配信
- 障害時は部分失敗を許容（1ツールが失敗しても他のフィードを壊さない）

**Tech stack:** Python 3.11+, feedgen, requests, BeautifulSoup4, PyYAML, pytest, responses, GitHub Actions, GitHub Pages

**Parallel execution:** Tasks 2–5 are independent and can be dispatched to parallel subagents after Task 1 completes. Task 6 (orchestrator) requires Tasks 2–5 to be complete. Task 7 (GitHub Actions + Pages) requires Task 6.

**Recommended execution order:**
1. Task 1: Scaffold (sequential, foundation for all others)
2. Tasks 2–5: Run in parallel subagents (each is independent)
3. Task 6: Main orchestrator (after 2–5)
4. Task 7: GitHub Actions + Pages (after 6)

---

## Task 1: プロジェクト構造のセットアップ

**Files:**
- Create: `tools/tools.yml`
- Create: `data/.gitkeep`
- Create: `feeds/.gitkeep`
- Create: `scripts/__init__.py`
- Create: `scripts/collectors/__init__.py`
- Create: `tests/__init__.py`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Modify: `.gitignore`

- [ ] **Step 1: ディレクトリ構造を作成する**

  Run:
  ```bash
  mkdir -p tools data feeds scripts/collectors tests
  touch scripts/__init__.py scripts/collectors/__init__.py tests/__init__.py data/.gitkeep feeds/.gitkeep
  ```

- [ ] **Step 2: requirements.txt を作成する**

  `requirements.txt`:
  ```
  requests>=2.31.0
  feedgen>=0.9.0
  PyYAML>=6.0.0
  beautifulsoup4>=4.12.0
  lxml>=4.9.3
  ```

  `requirements-dev.txt`:
  ```
  -r requirements.txt
  pytest>=7.4.0
  pytest-mock>=3.12.0
  responses>=0.24.0
  ```

- [ ] **Step 3: tools/tools.yml を作成する**

  `tools/tools.yml`:
  ```yaml
  tools:
    - id: trivy
      name: Trivy
      type: github
      repo: aquasecurity/trivy

    - id: grype
      name: Grype
      type: github
      repo: anchore/grype

    - id: syft
      name: Syft
      type: github
      repo: anchore/syft

    - id: osv-scanner
      name: OSV-Scanner
      type: github
      repo: google/osv-scanner

    - id: dependency-check
      name: Dependency-Check
      type: github
      repo: jeremylong/DependencyCheck

    - id: clair
      name: Clair
      type: github
      repo: quay/clair

    - id: vuls
      name: Vuls
      type: github
      repo: future-architect/vuls

    - id: futurevuls
      name: FutureVuls
      type: scrape_futurevuls
      url: https://help.vuls.biz/releasenotes/

    - id: yamory
      name: Yamory
      type: scrape_yamory
      url: https://yamory.io/news
  ```

- [ ] **Step 4: .gitignore を更新する**

  `.gitignore` に以下を追加する（既存の内容を壊さずに）:
  ```
  __pycache__/
  *.pyc
  .pytest_cache/
  .venv/
  *.egg-info/
  dist/
  ```

- [ ] **Step 5: 依存関係をインストールする**

  Run:
  ```bash
  pip install -r requirements-dev.txt
  ```

  Expected: `Successfully installed ...` のメッセージが出る

- [ ] **Step 6: コミットする**

  Run:
  ```bash
  git add -A
  git commit -m "chore: project scaffold - directories, tool config, and requirements"
  ```

---

## Task 2: データモデルと共通ストレージユーティリティ

**Files:**
- Create: `scripts/models.py`
- Create: `scripts/storage.py`
- Create: `tests/test_storage.py`

- [ ] **Step 1: テストを書く**

  `tests/test_storage.py`:
  ```python
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
  ```

- [ ] **Step 2: テストが失敗することを確認する**

  Run:
  ```bash
  pytest tests/test_storage.py -v
  ```

  Expected: `ImportError` または `ModuleNotFoundError`

- [ ] **Step 3: scripts/models.py を実装する**

  `scripts/models.py`:
  ```python
  from dataclasses import dataclass, asdict
  from typing import Literal

  Category = Literal["feature", "pricing", "security", "bugfix", "announcement", "other"]


  @dataclass
  class ReleaseEntry:
      tool_id: str
      tool_name: str
      version: str
      published_at: str  # ISO 8601 (e.g. "2024-01-15T10:00:00Z")
      url: str
      summary: str
      body: str
      category: Category

      def to_dict(self) -> dict:
          return asdict(self)

      @classmethod
      def from_dict(cls, d: dict) -> "ReleaseEntry":
          return cls(**d)
  ```

- [ ] **Step 4: scripts/storage.py を実装する**

  `scripts/storage.py`:
  ```python
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
      """新しいエントリを既存エントリにマージする（URLで重複排除、新しいものを先頭に）。"""
      existing_urls = {e.url for e in existing}
      truly_new = [e for e in new if e.url not in existing_urls]
      return truly_new + existing
  ```

- [ ] **Step 5: テストが通ることを確認する**

  Run:
  ```bash
  pytest tests/test_storage.py -v
  ```

  Expected:
  ```
  tests/test_storage.py::test_save_and_load_entries PASSED
  tests/test_storage.py::test_load_entries_returns_empty_list_when_file_missing PASSED
  tests/test_storage.py::test_merge_entries_deduplicates_by_url PASSED
  tests/test_storage.py::test_merge_entries_prepends_new_entries PASSED
  tests/test_storage.py::test_save_entries_is_atomic PASSED
  5 passed
  ```

- [ ] **Step 6: コミットする**

  Run:
  ```bash
  git add scripts/models.py scripts/storage.py tests/test_storage.py
  git commit -m "feat: data model and atomic JSON storage utilities"
  ```

---

## Task 3: リリース種別カテゴリ分類器

**Files:**
- Create: `scripts/categorize.py`
- Create: `tests/test_categorize.py`

- [ ] **Step 1: テストを書く**

  `tests/test_categorize.py`:
  ```python
  from scripts.categorize import classify_release


  def test_security_keyword_in_title():
      assert classify_release("security fix for CVE-2024-1234", "", "github") == "security"


  def test_cve_pattern():
      assert classify_release("fix CVE-2024-9999", "patch", "github") == "security"


  def test_hotfix_futurevuls():
      assert classify_release("[Hotfix] critical patch", "", "scrape_futurevuls") == "security"


  def test_pricing_keyword_japanese():
      assert classify_release("料金プランの変更について", "", "scrape_yamory") == "pricing"


  def test_bugfix_keyword():
      assert classify_release("bug fix release", "fixed a crash", "github") == "bugfix"


  def test_feature_keyword():
      assert classify_release("feat: add new scanner", "## Features", "github") == "feature"


  def test_announcement_yamory():
      assert classify_release("Security Days 2024 出展のお知らせ", "", "scrape_yamory") == "announcement"


  def test_regular_release_futurevuls_defaults_to_feature():
      assert classify_release("定期リリース", "バグ修正と機能追加", "scrape_futurevuls") == "feature"


  def test_empty_inputs_return_other():
      assert classify_release("", "", "github") == "other"


  def test_security_takes_priority_over_bugfix():
      assert classify_release("security bugfix", "fix CVE-2024-0001", "github") == "security"
  ```

- [ ] **Step 2: テストが失敗することを確認する**

  Run:
  ```bash
  pytest tests/test_categorize.py -v
  ```

  Expected: `ImportError` または `ModuleNotFoundError`

- [ ] **Step 3: scripts/categorize.py を実装する**

  `scripts/categorize.py`:
  ```python
  import re
  from scripts.models import Category

  # キーワードパターン（優先度順: security > pricing > bugfix > announcement > feature）
  _SECURITY_PATTERNS = [
      r"(?i)(security|cve-\d{4}-\d+|hotfix|hot.?fix|critical|vulnerability|脆弱性|セキュリティ)",
      r"(?i)\[重要\]",
  ]
  _PRICING_PATTERNS = [
      r"(?i)(pricing|price change|料金|価格|プラン変更)",
  ]
  _BUGFIX_PATTERNS = [
      r"(?i)(bug.?fix|bugfix|\bfix:|fixed\b|patch|不具合修正|修正)",
  ]
  _ANNOUNCEMENT_PATTERNS = [
      r"(?i)(出展|登壇|受賞|セミナー|お知らせ|award|summit|conference|導入|採用)",
  ]
  _FEATURE_PATTERNS = [
      r"(?i)(feat:|feature|機能追加|機能変更|新機能|リリース|release)",
  ]


  def classify_release(title: str, body: str, source_type: str) -> Category:
      """タイトルとボディのキーワードからリリース種別カテゴリを分類する。"""
      text = f"{title}\n{body}"
      if not text.strip():
          return "other"

      for pattern in _SECURITY_PATTERNS:
          if re.search(pattern, text):
              return "security"

      for pattern in _PRICING_PATTERNS:
          if re.search(pattern, text):
              return "pricing"

      for pattern in _BUGFIX_PATTERNS:
          if re.search(pattern, text):
              return "bugfix"

      # SaaS系は告知パターンをfeatureより優先して検出
      if source_type in ("scrape_yamory", "scrape_futurevuls"):
          for pattern in _ANNOUNCEMENT_PATTERNS:
              if re.search(pattern, text):
                  return "announcement"

      for pattern in _FEATURE_PATTERNS:
          if re.search(pattern, text):
              return "feature"

      # SaaS系のデフォルトはfeature（定期リリース等）
      if source_type in ("scrape_yamory", "scrape_futurevuls"):
          return "feature"

      return "other"
  ```

- [ ] **Step 4: テストが通ることを確認する**

  Run:
  ```bash
  pytest tests/test_categorize.py -v
  ```

  Expected: `10 passed`

- [ ] **Step 5: コミットする**

  Run:
  ```bash
  git add scripts/categorize.py tests/test_categorize.py
  git commit -m "feat: keyword-based release category classifier"
  ```

---

## Task 4: GitHub Releases API コレクター

**Files:**
- Create: `scripts/collectors/github.py`
- Create: `tests/test_collector_github.py`

**Depends on:** Task 2 (models, storage), Task 3 (categorize)

- [ ] **Step 1: テストを書く**

  `tests/test_collector_github.py`:
  ```python
  import responses

  from scripts.collectors.github import collect_github_releases

  MOCK_RELEASES = [
      {
          "tag_name": "v0.50.0",
          "published_at": "2024-01-15T10:00:00Z",
          "html_url": "https://github.com/aquasecurity/trivy/releases/tag/v0.50.0",
          "name": "Trivy v0.50.0",
          "body": "## Changes\n- feat: add new scanner",
      },
      {
          "tag_name": "v0.49.0",
          "published_at": "2023-12-01T10:00:00Z",
          "html_url": "https://github.com/aquasecurity/trivy/releases/tag/v0.49.0",
          "name": "Trivy v0.49.0",
          "body": "## Bug Fixes\n- fix: memory leak",
      },
  ]


  @responses.activate
  def test_collect_github_releases_returns_entries():
      responses.add(
          responses.GET,
          "https://api.github.com/repos/aquasecurity/trivy/releases",
          json=MOCK_RELEASES,
          status=200,
      )
      entries = collect_github_releases(
          tool_id="trivy",
          tool_name="Trivy",
          repo="aquasecurity/trivy",
          github_token=None,
      )
      assert len(entries) == 2
      assert entries[0].version == "v0.50.0"
      assert entries[0].tool_id == "trivy"
      assert entries[0].tool_name == "Trivy"
      assert entries[0].url == "https://github.com/aquasecurity/trivy/releases/tag/v0.50.0"
      assert entries[0].category in ("feature", "bugfix", "security", "other", "announcement", "pricing")


  @responses.activate
  def test_collect_github_releases_returns_empty_on_404():
      responses.add(
          responses.GET,
          "https://api.github.com/repos/unknown/notfound/releases",
          json={"message": "Not Found"},
          status=404,
      )
      entries = collect_github_releases(
          tool_id="notfound",
          tool_name="NotFound",
          repo="unknown/notfound",
          github_token=None,
      )
      assert entries == []


  @responses.activate
  def test_collect_github_releases_returns_empty_on_rate_limit():
      responses.add(
          responses.GET,
          "https://api.github.com/repos/aquasecurity/trivy/releases",
          status=429,
      )
      entries = collect_github_releases(
          tool_id="trivy",
          tool_name="Trivy",
          repo="aquasecurity/trivy",
          github_token=None,
      )
      assert entries == []


  @responses.activate
  def test_collect_github_releases_uses_token_in_header():
      responses.add(
          responses.GET,
          "https://api.github.com/repos/aquasecurity/trivy/releases",
          json=MOCK_RELEASES,
          status=200,
      )
      collect_github_releases(
          tool_id="trivy",
          tool_name="Trivy",
          repo="aquasecurity/trivy",
          github_token="test-token",
      )
      assert responses.calls[0].request.headers.get("Authorization") == "Bearer test-token"
  ```

- [ ] **Step 2: テストが失敗することを確認する**

  Run:
  ```bash
  pytest tests/test_collector_github.py -v
  ```

  Expected: `ImportError` または `ModuleNotFoundError`

- [ ] **Step 3: scripts/collectors/github.py を実装する**

  `scripts/collectors/github.py`:
  ```python
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
  ```

- [ ] **Step 4: テストが通ることを確認する**

  Run:
  ```bash
  pytest tests/test_collector_github.py -v
  ```

  Expected: `4 passed`

- [ ] **Step 5: コミットする**

  Run:
  ```bash
  git add scripts/collectors/github.py tests/test_collector_github.py
  git commit -m "feat: GitHub Releases API collector with partial failure handling"
  ```

---

## Task 5: SaaSコレクター（FutureVuls・Yamory）

**Files:**
- Create: `scripts/collectors/futurevuls.py`
- Create: `scripts/collectors/yamory.py`
- Create: `tests/test_collector_saas.py`

**Depends on:** Task 2 (models), Task 3 (categorize)

- [ ] **Step 1: テストを書く**

  `tests/test_collector_saas.py`:
  ```python
  import responses

  from scripts.collectors.futurevuls import collect_futurevuls
  from scripts.collectors.yamory import collect_yamory

  FUTUREVULS_HTML = """
  <html><body>
  <h2>2026年</h2>
  <ul>
    <li><a href="/releasenotes/20260224/">2026-02-24</a>：定期リリース</li>
    <li><a href="/releasenotes/20260101_hotfix/">[Hotfix] 2026-01-01</a></li>
  </ul>
  </body></html>
  """

  YAMORY_HTML = """
  <html><body>
  <ul class="news-list">
    <li>
      <h3><a href="/news/google-cloud-integration">Google Cloud 組織連携機能をリリース</a></h3>
      <h4>2026-03-31</h4>
    </li>
    <li>
      <h3><a href="/news/security-days-2026">Security Days Spring 2026 出展のお知らせ</a></h3>
      <h4>2026-02-26</h4>
    </li>
  </ul>
  </body></html>
  """


  @responses.activate
  def test_collect_futurevuls_returns_entries():
      responses.add(
          responses.GET,
          "https://help.vuls.biz/releasenotes/",
          body=FUTUREVULS_HTML,
          status=200,
      )
      entries = collect_futurevuls()
      assert len(entries) >= 1
      assert entries[0].tool_id == "futurevuls"
      assert entries[0].tool_name == "FutureVuls"
      assert "help.vuls.biz" in entries[0].url


  @responses.activate
  def test_collect_futurevuls_hotfix_categorized_as_security():
      responses.add(
          responses.GET,
          "https://help.vuls.biz/releasenotes/",
          body=FUTUREVULS_HTML,
          status=200,
      )
      entries = collect_futurevuls()
      hotfix_entries = [e for e in entries if "Hotfix" in e.summary or "hotfix" in e.url]
      assert any(e.category == "security" for e in hotfix_entries)


  @responses.activate
  def test_collect_futurevuls_returns_empty_on_error():
      responses.add(
          responses.GET,
          "https://help.vuls.biz/releasenotes/",
          status=500,
      )
      entries = collect_futurevuls()
      assert entries == []


  @responses.activate
  def test_collect_yamory_returns_entries():
      responses.add(
          responses.GET,
          "https://yamory.io/news",
          body=YAMORY_HTML,
          status=200,
      )
      entries = collect_yamory()
      assert len(entries) >= 1
      assert entries[0].tool_id == "yamory"
      assert entries[0].tool_name == "Yamory"
      assert "yamory.io" in entries[0].url


  @responses.activate
  def test_collect_yamory_announcement_categorized_correctly():
      responses.add(
          responses.GET,
          "https://yamory.io/news",
          body=YAMORY_HTML,
          status=200,
      )
      entries = collect_yamory()
      announcement_entries = [e for e in entries if "出展" in e.summary]
      assert any(e.category == "announcement" for e in announcement_entries)


  @responses.activate
  def test_collect_yamory_returns_empty_on_error():
      responses.add(
          responses.GET,
          "https://yamory.io/news",
          status=500,
      )
      entries = collect_yamory()
      assert entries == []
  ```

- [ ] **Step 2: テストが失敗することを確認する**

  Run:
  ```bash
  pytest tests/test_collector_saas.py -v
  ```

  Expected: `ImportError`

- [ ] **Step 3: scripts/collectors/futurevuls.py を実装する**

  `scripts/collectors/futurevuls.py`:
  ```python
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
  ```

- [ ] **Step 4: scripts/collectors/yamory.py を実装する**

  `scripts/collectors/yamory.py`:
  ```python
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
  ```

- [ ] **Step 5: テストが通ることを確認する**

  Run:
  ```bash
  pytest tests/test_collector_saas.py -v
  ```

  Expected: `6 passed`

- [ ] **Step 6: コミットする**

  Run:
  ```bash
  git add scripts/collectors/futurevuls.py scripts/collectors/yamory.py tests/test_collector_saas.py
  git commit -m "feat: SaaS collectors for FutureVuls and Yamory with error handling"
  ```

---

## Task 6: フィードジェネレーター（RSS / Atom / JSON Feed）

**Files:**
- Create: `scripts/feed_generator.py`
- Create: `tests/test_feed_generator.py`

**Depends on:** Task 2 (models)

- [ ] **Step 1: テストを書く**

  `tests/test_feed_generator.py`:
  ```python
  import json
  import xml.etree.ElementTree as ET

  from scripts.feed_generator import generate_atom, generate_json_feed, generate_rss
  from scripts.models import ReleaseEntry


  def make_entries():
      return [
          ReleaseEntry(
              tool_id="trivy",
              tool_name="Trivy",
              version="v0.50.0",
              published_at="2024-01-15T10:00:00Z",
              url="https://github.com/aquasecurity/trivy/releases/tag/v0.50.0",
              summary="Trivy v0.50.0",
              body="## Changes\n- feat: add new scanner",
              category="feature",
          ),
          ReleaseEntry(
              tool_id="grype",
              tool_name="Grype",
              version="v0.74.0",
              published_at="2024-01-10T10:00:00Z",
              url="https://github.com/anchore/grype/releases/tag/v0.74.0",
              summary="Grype v0.74.0",
              body="## Bug Fixes\n- fix: false positive",
              category="bugfix",
          ),
      ]


  def test_generate_rss_is_valid_xml():
      content = generate_rss(make_entries(), feed_title="SCA Tools Feed", feed_url="https://example.com/all.rss")
      root = ET.fromstring(content)
      assert root.tag == "rss"
      assert root.attrib.get("version") == "2.0"


  def test_generate_rss_contains_entries():
      content = generate_rss(make_entries(), feed_title="SCA Tools Feed", feed_url="https://example.com/all.rss")
      assert b"Trivy v0.50.0" in content
      assert b"Grype v0.74.0" in content


  def test_generate_rss_with_empty_entries():
      content = generate_rss([], feed_title="SCA Tools Feed", feed_url="https://example.com/all.rss")
      root = ET.fromstring(content)
      assert root.tag == "rss"


  def test_generate_atom_is_valid_xml():
      content = generate_atom(make_entries(), feed_title="SCA Tools Feed", feed_url="https://example.com/all.atom")
      root = ET.fromstring(content)
      assert "feed" in root.tag


  def test_generate_atom_contains_entries():
      content = generate_atom(make_entries(), feed_title="SCA Tools Feed", feed_url="https://example.com/all.atom")
      assert b"Trivy v0.50.0" in content


  def test_generate_json_feed_is_valid_json():
      content = generate_json_feed(make_entries(), feed_title="SCA Tools Feed", feed_url="https://example.com/all.json")
      data = json.loads(content)
      assert data["version"] == "https://jsonfeed.org/version/1.1"
      assert data["title"] == "SCA Tools Feed"
      assert len(data["items"]) == 2


  def test_generate_json_feed_contains_category_as_tag():
      content = generate_json_feed(make_entries(), feed_title="SCA Tools Feed", feed_url="https://example.com/all.json")
      data = json.loads(content)
      assert data["items"][0]["tags"] == ["feature"]
      assert data["items"][1]["tags"] == ["bugfix"]


  def test_generate_json_feed_contains_tool_id():
      content = generate_json_feed(make_entries(), feed_title="SCA Tools Feed", feed_url="https://example.com/all.json")
      data = json.loads(content)
      assert data["items"][0]["_tool_id"] == "trivy"
  ```

- [ ] **Step 2: テストが失敗することを確認する**

  Run:
  ```bash
  pytest tests/test_feed_generator.py -v
  ```

  Expected: `ImportError`

- [ ] **Step 3: scripts/feed_generator.py を実装する**

  `scripts/feed_generator.py`:
  ```python
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
  ```

- [ ] **Step 4: テストが通ることを確認する**

  Run:
  ```bash
  pytest tests/test_feed_generator.py -v
  ```

  Expected: `9 passed`

- [ ] **Step 5: コミットする**

  Run:
  ```bash
  git add scripts/feed_generator.py tests/test_feed_generator.py
  git commit -m "feat: RSS 2.0, Atom 1.0, JSON Feed 1.1 generators"
  ```

---

## Task 7: メインオーケストレーターとGitHub Actionsワークフロー

**Files:**
- Create: `scripts/main.py`
- Create: `.github/workflows/update-feeds.yml`
- Create: `feeds/index.html`
- Create: `feeds/.nojekyll`

**Depends on:** Tasks 2–6 (all)

- [ ] **Step 1: scripts/main.py を作成する**

  `scripts/main.py`:
  ```python
  #!/usr/bin/env python3
  """SCAツールのリリース情報を収集してフィードを生成するメインスクリプト。"""
  import logging
  import os
  import tempfile
  from pathlib import Path
  from typing import List

  import yaml

  from scripts.collectors.futurevuls import collect_futurevuls
  from scripts.collectors.github import collect_github_releases
  from scripts.collectors.yamory import collect_yamory
  from scripts.feed_generator import generate_atom, generate_json_feed, generate_rss
  from scripts.models import ReleaseEntry
  from scripts.storage import load_entries, merge_entries, save_entries

  logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
  logger = logging.getLogger(__name__)

  DATA_DIR = Path("data")
  FEEDS_DIR = Path("feeds")
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


  def main() -> None:
      github_token = os.environ.get("GITHUB_TOKEN")
      tools = load_tools_config()
      DATA_DIR.mkdir(exist_ok=True)

      all_entries: List[ReleaseEntry] = []
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

          all_entries.extend(merged)

      # 公開日時でソート（新しい順）
      all_entries.sort(key=lambda e: e.published_at, reverse=True)

      write_feeds(all_entries)

      if failed_tools:
          logger.warning("Failed to collect from: %s", ", ".join(failed_tools))

      logger.info("Done.")


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 2: .github/workflows/update-feeds.yml を作成する**

  `.github/workflows/update-feeds.yml`:
  ```yaml
  name: Update Feeds

  on:
    schedule:
      - cron: "0 1 * * *"  # 毎日 UTC 01:00 (JST 10:00)
    workflow_dispatch:       # 手動実行も可能

  permissions:
    contents: write
    issues: write            # 失敗時のIssue作成に必要

  jobs:
    update:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4

        - name: Set up Python
          uses: actions/setup-python@v5
          with:
            python-version: "3.11"
            cache: "pip"

        - name: Install dependencies
          run: pip install -r requirements.txt

        - name: Collect and generate feeds
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
            FEED_BASE_URL: "https://tmyymmt.github.io/sca-tools-feed/feeds"
          run: python -m scripts.main

        - name: Commit and push if changed
          run: |
            git config user.name "github-actions[bot]"
            git config user.email "github-actions[bot]@users.noreply.github.com"
            git add data/ feeds/
            git diff --staged --quiet || git commit -m "chore: update feeds $(date -u +'%Y-%m-%d')"
            git push

        - name: Create issue on consecutive failure
          if: failure()
          uses: actions/github-script@v7
          with:
            script: |
              const title = `Feed update failed on ${new Date().toISOString().split('T')[0]}`;
              const existing = await github.rest.issues.listForRepo({
                owner: context.repo.owner,
                repo: context.repo.repo,
                state: 'open',
                labels: ['feed-failure'],
              });
              if (existing.data.length === 0) {
                await github.rest.issues.create({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  title,
                  body: `The daily feed update workflow failed.\n\n[See run](${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId})`,
                  labels: ['feed-failure'],
                });
              }
  ```

- [ ] **Step 3: feeds/index.html を作成する（GitHub Pages用）**

  `feeds/index.html`:
  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SCA Tools Feed</title>
    <style>
      body { font-family: sans-serif; max-width: 860px; margin: 2em auto; padding: 0 1em; line-height: 1.6; }
      h1 { border-bottom: 2px solid #333; padding-bottom: 0.3em; }
      h2 { margin-top: 1.5em; }
      table { border-collapse: collapse; width: 100%; }
      th, td { border: 1px solid #ccc; padding: 0.5em 1em; text-align: left; }
      th { background: #f5f5f5; }
      a { color: #0066cc; }
      code { background: #f0f0f0; padding: 0.1em 0.3em; border-radius: 3px; }
    </style>
  </head>
  <body>
    <h1>SCA Tools Feed</h1>
    <p>Release information feeds for SCA (Software Composition Analysis) tools.</p>
    <p>Updated daily via GitHub Actions. Subscribe with any RSS reader.</p>

    <h2>All Tools (Combined)</h2>
    <table>
      <tr><th>Format</th><th>URL</th></tr>
      <tr><td>RSS 2.0</td><td><a href="all.rss">all.rss</a></td></tr>
      <tr><td>Atom 1.0</td><td><a href="all.atom">all.atom</a></td></tr>
      <tr><td>JSON Feed 1.1</td><td><a href="all.json">all.json</a></td></tr>
    </table>

    <h2>Per-Tool Feeds</h2>
    <table>
      <tr><th>Tool</th><th>RSS</th><th>Atom</th><th>JSON Feed</th></tr>
      <tr><td>Trivy</td><td><a href="trivy.rss">trivy.rss</a></td><td><a href="trivy.atom">trivy.atom</a></td><td><a href="trivy.json">trivy.json</a></td></tr>
      <tr><td>Grype</td><td><a href="grype.rss">grype.rss</a></td><td><a href="grype.atom">grype.atom</a></td><td><a href="grype.json">grype.json</a></td></tr>
      <tr><td>Syft</td><td><a href="syft.rss">syft.rss</a></td><td><a href="syft.atom">syft.atom</a></td><td><a href="syft.json">syft.json</a></td></tr>
      <tr><td>OSV-Scanner</td><td><a href="osv-scanner.rss">osv-scanner.rss</a></td><td><a href="osv-scanner.atom">osv-scanner.atom</a></td><td><a href="osv-scanner.json">osv-scanner.json</a></td></tr>
      <tr><td>Dependency-Check</td><td><a href="dependency-check.rss">dependency-check.rss</a></td><td><a href="dependency-check.atom">dependency-check.atom</a></td><td><a href="dependency-check.json">dependency-check.json</a></td></tr>
      <tr><td>Clair</td><td><a href="clair.rss">clair.rss</a></td><td><a href="clair.atom">clair.atom</a></td><td><a href="clair.json">clair.json</a></td></tr>
      <tr><td>Vuls (OSS)</td><td><a href="vuls.rss">vuls.rss</a></td><td><a href="vuls.atom">vuls.atom</a></td><td><a href="vuls.json">vuls.json</a></td></tr>
      <tr><td>FutureVuls</td><td><a href="futurevuls.rss">futurevuls.rss</a></td><td><a href="futurevuls.atom">futurevuls.atom</a></td><td><a href="futurevuls.json">futurevuls.json</a></td></tr>
      <tr><td>Yamory</td><td><a href="yamory.rss">yamory.rss</a></td><td><a href="yamory.atom">yamory.atom</a></td><td><a href="yamory.json">yamory.json</a></td></tr>
    </table>
  </body>
  </html>
  ```

- [ ] **Step 4: GitHub Pages用 .nojekyll を作成する**

  Run:
  ```bash
  touch feeds/.nojekyll
  ```

- [ ] **Step 5: 全テストが通ることを確認する**

  Run:
  ```bash
  pytest tests/ -v
  ```

  Expected: 全テストが `passed`（失敗があれば修正する）

- [ ] **Step 6: ローカル動作確認（GITHUB_TOKENなし）**

  Run:
  ```bash
  python -m scripts.main
  ```

  Expected: `data/` にJSONファイルが生成され、`feeds/` にRSS/Atom/JSONファイルが生成される。GitHub APIレートリミット（未認証: 60req/h）で一部ツールが失敗しても、他のツールのフィードは正常生成される。

- [ ] **Step 7: コミットしてプッシュする**

  Run:
  ```bash
  git add -A
  git commit -m "feat: main orchestrator, GitHub Actions workflow, and GitHub Pages index"
  git push
  ```

- [ ] **Step 8: GitHub Pages を有効化する**

  GitHub.com → リポジトリ Settings → Pages → Source を選択:
  - **Branch:** `main`
  - **Folder:** `/feeds`

  設定後、`https://tmyymmt.github.io/sca-tools-feed/` でフィードが公開される。

---

## 完了後の確認チェックリスト

- [ ] `pytest tests/ -v` で全テストが `passed`
- [ ] `python -m scripts.main` が正常終了し `feeds/all.rss`, `feeds/all.atom`, `feeds/all.json` が生成される
- [ ] GitHub Actions ワークフローが `workflow_dispatch` で手動実行できる
- [ ] GitHub Pages で `https://tmyymmt.github.io/sca-tools-feed/` が公開される
- [ ] RSSリーダーで `https://tmyymmt.github.io/sca-tools-feed/feeds/all.rss` が購読できる
