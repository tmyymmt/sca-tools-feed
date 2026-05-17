# sca-tools-feed

セキュリティ／脆弱性スキャンツールのリリース情報を集約し、各ツールごとのまとめページと比較ページを HTML として生成し、フィードとして公開するリポジトリです。

## 対象ツールの種類

本リポジトリが扱うのは、**SCA（Software Composition Analysis）ツール**、すなわち**SBOMベースの脆弱性管理ツール**です。

具体的には、システムを構成するOSパッケージ・ライブラリ・コンテナイメージ等をスキャンしてSBOM（Software Bill of Materials）を生成し、そのSBOMと日々更新されるCVE等の脆弱性情報をマッチングすることで、既知の脆弱性を検出するツールを対象とします。

以下のカテゴリのツールは対象外です：

- **静的コード解析（SAST）**：ソースコードの記述パターンから脆弱性を検出するツール（例：SonarQube、Semgrep）
- **動的脆弱性スキャン（DAST）**：実行中のシステムにリクエストを送信して脆弱性を検出するツール（例：OWASP ZAP）
- **SBOMの生成・管理のみを行うツール**：CVEとのマッチングを行わないもの（例：microsoft/sbom-tool）

## 公開サイト

https://tmyymmt.github.io/sca-tools-feed/ で GitHub Pages として公開されています。フィード一覧・各ツールまとめページ・比較ページを閲覧できます。HTML ページはすべて `prefers-color-scheme` によるダークモードに対応しています。

## 動作原理

- 以下のいずれかの方法でフィードファイルを更新し、HTML ページ（Markdown ソースから生成）をレンダリングする
  - github actionsで日次で実行
  - Issueを作成し、copilotでPRを作成、レビューを完了し、mainにマージ

## ファイル構成

### Spec テンプレート

- GitHub Spec Kit 形式の機能仕様テンプレート: `.specify/templates/spec-template.md`

### 全仕様書

- docs/fulls-specs/spec_ja.md
- 全仕様書は常に最新の仕様を記載する
- 機能改修時に全仕様書も更新する

## ルール
  
- ドキュメントは日本語と英語の両方を作成する
  - 英語は `*.md` 、日本語は `*_ja.md` とする

## ライセンス

MIT License
