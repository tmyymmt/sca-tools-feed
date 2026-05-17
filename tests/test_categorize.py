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
