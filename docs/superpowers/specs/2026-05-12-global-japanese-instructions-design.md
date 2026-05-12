# 設計書: Copilot CLI グローバル日本語応答設定

**日付:** 2026-05-12  
**対象:** Copilot CLI（ターミナル）の全リポジトリ共通設定

---

## 概要

Copilot CLI が全リポジトリで日本語で応答するよう、グローバル指示ファイルを作成する。
コードやコマンドは英語のまま維持し、会話・説明文のみ日本語で統一する。

---

## 対象ファイル

| ファイル | 種別 | 用途 |
|---|---|---|
| `~/.copilot/copilot-instructions.md` | 新規作成 | 全リポジトリ共通の言語指示 |

---

## 設定内容

`~/.copilot/copilot-instructions.md` に以下を記載する:

```markdown
- 会話・説明・コメントはすべて日本語で応答する
- コード・コマンド・ファイルパス・変数名などは英語のまま維持する
```

---

## 動作仕様

- Copilot CLI は起動時に `~/.copilot/copilot-instructions.md` を自動で読み込む
- 各リポジトリの `.github/copilot-instructions.md` と **併用**される（上書きではなく合成）
- 既存のリポジトリ固有ルール（例: `README.md` は英語で書く）はそのまま有効

---

## スコープ外

- VS Code Copilot Chat の言語設定（別途 `github.copilot.chat.localeOverride` で設定可）
- コード・コマンド・ファイルパス・変数名の日本語化（英語のまま維持）

---

## 実装手順

1. `~/.copilot/copilot-instructions.md` を作成し、日本語応答の指示を記載する
