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

FUTUREVULS_PAGE_HTML = """
<html><body>
<article>
<h1>2026-02-24 リリース内容</h1>
<p>新機能が追加されました。スキャナのアップデートが必要です。</p>
</article>
</body></html>
"""

FUTUREVULS_HOTFIX_PAGE_HTML = """
<html><body>
<article>
<h1>[Hotfix] 2026-01-01</h1>
<p>セキュリティ修正が含まれています。</p>
</article>
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


def _add_futurevuls_page_mocks():
    responses.add(
        responses.GET,
        "https://help.vuls.biz/releasenotes/20260224/",
        body=FUTUREVULS_PAGE_HTML,
        status=200,
    )
    responses.add(
        responses.GET,
        "https://help.vuls.biz/releasenotes/20260101_hotfix/",
        body=FUTUREVULS_HOTFIX_PAGE_HTML,
        status=200,
    )


@responses.activate
def test_collect_futurevuls_returns_entries():
    responses.add(
        responses.GET,
        "https://help.vuls.biz/releasenotes/",
        body=FUTUREVULS_HTML,
        status=200,
    )
    _add_futurevuls_page_mocks()
    entries = collect_futurevuls()
    assert len(entries) >= 1
    assert entries[0].tool_id == "futurevuls"
    assert entries[0].tool_name == "FutureVuls"
    assert "help.vuls.biz" in entries[0].url


@responses.activate
def test_collect_futurevuls_body_contains_page_content():
    responses.add(
        responses.GET,
        "https://help.vuls.biz/releasenotes/",
        body=FUTUREVULS_HTML,
        status=200,
    )
    _add_futurevuls_page_mocks()
    entries = collect_futurevuls()
    regular = next(e for e in entries if "hotfix" not in e.url)
    assert "新機能" in regular.body or "スキャナ" in regular.body


@responses.activate
def test_collect_futurevuls_hotfix_categorized_as_security():
    responses.add(
        responses.GET,
        "https://help.vuls.biz/releasenotes/",
        body=FUTUREVULS_HTML,
        status=200,
    )
    _add_futurevuls_page_mocks()
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
