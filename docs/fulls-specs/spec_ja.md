# 全仕様

このディレクトリ以下に本プロジェクトの全仕様を記述する。

## 全仕様の記述方針

- 仕様の全体には本ファイルを起点として辿れるようにする
- 1ファイルが巨大にならないようにする
  - 適切に記述内容の抽象化の度合いを調整する
  - 適切な単位でファイルを分割する
- 子ファイルを作成する場合
  - 前提情報のファイルへのリンクを付けること

---

## 1. 対象ツール

### 調査対象

| ツール | 種別 | 情報源 | 取得方法 |
|---|---|---|---|
| FutureVuls | SaaS（脆弱性管理） | https://help.vuls.biz/releasenotes/ | GitHub Actions + Copilot web検索 or HTMLスクレイピング |
| Vuls（OSS版） | OSS | https://github.com/future-architect/vuls | GitHub Releases API |
| Yamory | SaaS（脆弱性管理） | https://yamory.io/news | GitHub Actions + Copilot web検索 or HTMLスクレイピング |
| Trivy | OSS | https://github.com/aquasecurity/trivy | GitHub Releases API + CHANGELOG.md |
| Grype | OSS | https://github.com/anchore/grype | GitHub Releases API |
| Syft | OSS | https://github.com/anchore/syft | GitHub Releases API |
| OSV-Scanner | OSS | https://github.com/google/osv-scanner | GitHub Releases API |
| Dependency-Check | OSS | https://github.com/jeremylong/DependencyCheck | GitHub Releases API |
| Clair | OSS | https://github.com/quay/clair | GitHub Releases API |

### 対象外（参考記述のみ）

SBOMの生成・管理のみを行うツールは調査対象外とする。参考としてリンクのみ記載する。

- [microsoft/sbom-tool](https://github.com/microsoft/sbom-tool)

---

## 2. フィード仕様

### フォーマット

- RSS 2.0
- Atom 1.0
- JSON Feed 1.1

の3形式すべてに対応する。

### 含める情報項目

- バージョン（タグ名）
- 日時（公開日時）
- URL（リリースページへのリンク）
- サマリ（タイトル・概要）
- 変更内容（CHANGELOG / リリースノート本文）
- リリース種別カテゴリ（後述）

### リリース種別カテゴリ

フィードはリリース種別でカテゴリ分けする。フィルタリングにも使用する。

- `feature`：機能追加・変更（最優先）
- `pricing`：料金変更
- `security`：セキュリティ修正・Hotfix
- `bugfix`：バグ修正
- `announcement`：告知・登壇・受賞等（yamory等のSaaS向け）
- `other`：その他

### 更新頻度

- GitHub Actions で日次実行
- または Issue 作成 → Copilot によるPR作成 → レビュー → mainマージ

### 公開エンドポイント

- GitHub Pages で公開

---

## 3. データ収集

### 収集方式

| 対象種別 | 方法 |
|---|---|
| GitHub OSS（Trivy 等） | GitHub Actions + GitHub Releases API（構造化データ取得可） |
| SaaS（FutureVuls・Yamory） | GitHub Actions + Copilot web検索 or HTMLスクレイピング |

### GitHub Releases API

- エンドポイント：`https://api.github.com/repos/{owner}/{repo}/releases`
- 取得可能なフィールド：`tag_name`（バージョン）、`published_at`（日時）、`body`（CHANGELOG相当）、`html_url`
- レート制限：未認証60req/時、トークンあり5000req/時
- **APIを優先し、スクレイピングは最終手段とする**（HTML変更で壊れやすいため）

### 実行方式

- ポーリング（日次定期実行）を基本とする
- イベント駆動（GitHub webhook等）は対象SaaSが非対応のため採用しない

---

## 4. データ保存・管理

- 収集データはリポジトリ内ファイルとして保存（JSONの中間形式）
- 各ソースから取得したデータをJSON（中間形式）で統一して保存し、そこからRSS/Atom/JSON Feedを生成する
  - ソース変更時の影響範囲を最小化できる
- 履歴は永久に保持・蓄積する（削除しない）
- 対象ツールはYAML等の設定ファイルで管理し、コード変更なしで追加できる構造にする

---

## 5. 公開・配信

- 対象ユーザー：不特定多数
- 購読方法：RSSリーダー、またはリポジトリのファイルを直接参照
- フィルタリング：リリース種別カテゴリで絞り込み可能

---

## 6. 非機能要件

### メンテナンス負荷の低減

- スクレイピングより GitHub API を優先する
- 対象ツール数はGitHub APIで取れるOSSは増やしやすいが、スクレイピングが必要なSaaSは慎重に追加する
- 内部データ形式をJSONで統一し、ソース変更時の影響を限定する
- 設定ファイル（YAML等）でツール一覧を管理し、コード変更なしで新規ツールを追加できる構造にする
- スクレイピング対象のHTMLが想定外に変化した場合は警告を出すが、フィードは壊さない

### 障害時の挙動

| 観点 | 挙動 |
|---|---|
| 部分失敗 | 1ツールの収集が失敗しても、他のツールのフィードは更新する |
| アトミック書き込み | 一時ファイルに書いてから rename。中途半端な状態のファイルを公開しない |
| レート制限 | GitHub API の 429 を受けたらその実行をスキップし、次回に持ち越す |
| 404/ページ消滅 | ツールが公開をやめた場合、エラーログに記録し既存データはそのまま保持する |
| GitHub Actions 通知 | 連続N回失敗したら Issue を自動作成してアラートを出す |
| フィード形式の検証 | 生成したRSS/Atom/JSON FeedをXMLパース・スキーマ検証してから公開する |
| ロールバック | Git リポジトリにデータを持つため、破損時は `git revert` で戻せる |

### ライセンス

MIT License
