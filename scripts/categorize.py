import re
from scripts.models import Category

# キーワードパターン（優先度順: security > pricing > bugfix > announcement > feature）
# "security" 単体はイベント名等と区別するため、文脈が必要
_SECURITY_PATTERNS = [
    r"(?i)(cve-\d{4}-\d+|hotfix|hot.?fix|critical|vulnerability|脆弱性|セキュリティ)",
    r"(?i)\[重要\]",
    r"(?i)security.{0,30}(fix|patch|vulnerab|advisory|update|alert|bug)",
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

    if source_type in ("scrape_yamory", "scrape_futurevuls"):
        # SaaS系: 告知 > feature > bugfix の順で判定（定期リリースはfeature優先）
        for pattern in _ANNOUNCEMENT_PATTERNS:
            if re.search(pattern, text):
                return "announcement"
        for pattern in _FEATURE_PATTERNS:
            if re.search(pattern, text):
                return "feature"
        for pattern in _BUGFIX_PATTERNS:
            if re.search(pattern, text):
                return "bugfix"
        return "feature"

    # 非SaaS (e.g., github): bugfix > feature > other
    for pattern in _BUGFIX_PATTERNS:
        if re.search(pattern, text):
            return "bugfix"

    for pattern in _FEATURE_PATTERNS:
        if re.search(pattern, text):
            return "feature"

    return "other"
