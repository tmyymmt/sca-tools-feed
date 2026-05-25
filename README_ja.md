# SCA Tools Feed

セキュリティ／脆弱性スキャンツールのリリース情報を集約し、各ツールごとのまとめページと比較ページを HTML として生成し、フィードとして公開するリポジトリです。

GitHub Actions により毎週自動更新されます。生成されるフィードは任意のRSSリーダーで購読できます。

🌐 **公開サイト**: https://tmyymmt.github.io/sca-tools-feed/

## 対象ツールのカテゴリ

本リポジトリが扱うのは、**SCA（Software Composition Analysis）ツール**、すなわち**SBOMベースの脆弱性管理ツール**です。

具体的には、システムを構成するOSパッケージ・ライブラリ・コンテナイメージ等をスキャンしてSBOM（Software Bill of Materials）を生成し、そのSBOMと日々更新されるCVE等の脆弱性情報をマッチングすることで、既知の脆弱性を検出するツールを対象とします。

以下のカテゴリのツールは対象外です：

- **静的コード解析（SAST）**：ソースコードの記述パターンから脆弱性を検出するツール（例：SonarQube、Semgrep）。関連リポジトリ: https://github.com/tmyymmt/sast-tools-feed/
- **動的脆弱性スキャン（DAST）**：実行中のシステムにリクエストを送信して脆弱性を検出するツール（例：OWASP ZAP）。関連リポジトリ: https://github.com/tmyymmt/dast-tools-feed/
- **SBOMの生成・管理のみを行うツール**：CVEとのマッチングを行わないもの（例：microsoft/sbom-tool）

## 動作原理

- 以下のいずれかの方法でフィードファイルを更新し、HTML ページ（Markdown ソースから生成）をレンダリングする
  - GitHub Actions で週次（毎週土曜 JST 07:00）で実行
  - Issue を作成し、Copilot で PR を作成、レビューを完了し、main にマージ

## 対象ツール

| ツール | 種別 | ライセンス |
|--------|------|----------|
| [Trivy](https://trivy.dev) | OSS | Apache-2.0 |
| [Grype](https://github.com/anchore/grype) | OSS | Apache-2.0 |
| [Syft](https://github.com/anchore/syft) | OSS | Apache-2.0 |
| [OSV-Scanner](https://google.github.io/osv-scanner/) | OSS | Apache-2.0 |
| [Dependency-Check](https://jeremylong.github.io/DependencyCheck/) | OSS | Apache-2.0 |
| [Clair](https://github.com/quay/clair) | OSS | Apache-2.0 |
| [Vuls](https://vuls.io) | OSS | GPL-3.0 |
| [FutureVuls](https://vuls.biz) | 商用 | Proprietary |
| [Yamory](https://yamory.io) | 商用 | Proprietary |

## フィード URL

### 全ツール統合

| フォーマット | URL |
|------------|-----|
| RSS 2.0 | `https://tmyymmt.github.io/sca-tools-feed/feeds/all.rss` |
| Atom 1.0 | `https://tmyymmt.github.io/sca-tools-feed/feeds/all.atom` |
| JSON Feed 1.1 | `https://tmyymmt.github.io/sca-tools-feed/feeds/all.json` |

### ツール別フィード

`{tool_id}` を `trivy`、`grype`、`syft`、`osv-scanner`、`dependency-check`、`clair`、`vuls`、`futurevuls`、`yamory` に置き換えてください。

| フォーマット | URL |
|------------|-----|
| RSS 2.0 | `https://tmyymmt.github.io/sca-tools-feed/feeds/{tool_id}.rss` |
| Atom 1.0 | `https://tmyymmt.github.io/sca-tools-feed/feeds/{tool_id}.atom` |
| JSON Feed 1.1 | `https://tmyymmt.github.io/sca-tools-feed/feeds/{tool_id}.json` |

## ページ

- **比較ページ**: [英語](https://tmyymmt.github.io/sca-tools-feed/comparison.html) / [日本語](https://tmyymmt.github.io/sca-tools-feed/comparison_ja.html)
- **ツール別まとめ**: `https://tmyymmt.github.io/sca-tools-feed/{tool_id}.html`

## リリースカテゴリ

リリースはカテゴリで分類され、フィルタリングに使用できます。

| カテゴリ | 説明 |
|---------|------|
| `feature` | 機能追加・変更 |
| `bugfix` | バグ修正 |
| `security` | セキュリティ修正・Hotfix |
| `pricing` | 料金変更 |
| `announcement` | 告知・イベント・受賞 |
| `other` | その他 |

## リポジトリ構成

### Spec テンプレート

- GitHub Spec Kit 形式の機能仕様テンプレート: `.specify/templates/spec-template.md`

### 全仕様書

- docs/full-specs/spec_ja.md
- 全仕様書は常に最新の仕様を記載する

## ルール
  
- ドキュメントは日本語と英語の両方を作成する
  - 英語は `*.md` 、日本語は `*_ja.md` とする
- 機能改修時に全仕様書も更新する
- AI向けのルールは .github/copilot-instructions.md に記載する

## セットアップ

### 前提条件

- Python 3.11 以上

### インストール

```bash
# 仮想環境の作成と有効化
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 依存ライブラリのインストール
pip install -r requirements.txt

# 開発用ライブラリのインストール（テスト実行時のみ）
pip install -r requirements-dev.txt
```

## ローカル実行

### 環境変数の設定

GitHub API を使用するため、`GITHUB_TOKEN` が必要です。

```bash
export GITHUB_TOKEN=your_github_token
```

### 実行

```bash
python -m scripts.main
```

`public/` 配下の HTML ファイルと `public/feeds/` 配下のフィードファイルが更新されます。

## GitHub Actions

### 自動実行（週次）

`.github/workflows/update-feeds.yml` により、毎週土曜日 JST 07:00（UTC 金曜 22:00）に自動実行されます。

### 手動実行

GitHub リポジトリの **Actions** タブ → **Update Feeds** → **Run workflow** から手動実行できます。

### 必要な設定

- **Secrets**: `GITHUB_TOKEN` は GitHub Actions により自動的に提供されるため、追加設定は不要です。
- **Permissions**: `contents: write`（データコミット用）、`pages: write`（GitHub Pages デプロイ用）が設定済みです。
- **GitHub Pages**: リポジトリの Settings → Pages から、Source を `GitHub Actions` に設定してください。

## ライセンス

MIT License
