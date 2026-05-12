# Copilot CLI グローバル日本語応答設定 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `~/.copilot/copilot-instructions.md` を作成し、Copilot CLI が全リポジトリで日本語（会話・説明）、英語（コード・コマンド）で応答するようにする。

**Architecture:** グローバル指示ファイルに言語ルールを2行記載するだけ。既存のリポジトリ固有設定は一切変更しない。

**Tech Stack:** Markdown

---

### Task 1: グローバル指示ファイルの作成と確認

**Files:**
- Create: `~/.copilot/copilot-instructions.md`

- [ ] **Step 1: ファイルが存在しないことを確認する**

Run:
```bash
ls ~/.copilot/copilot-instructions.md 2>&1
```

Expected: `No such file or directory`（すでに存在する場合は内容を確認してから追記する）

- [ ] **Step 2: グローバル指示ファイルを作成する**

以下の内容で `~/.copilot/copilot-instructions.md` を作成する:

```markdown
- 会話・説明・コメントはすべて日本語で応答する
- コード・コマンド・ファイルパス・変数名などは英語のまま維持する
```

Run:
```bash
cat > ~/.copilot/copilot-instructions.md << 'EOF'
- 会話・説明・コメントはすべて日本語で応答する
- コード・コマンド・ファイルパス・変数名などは英語のまま維持する
EOF
```

- [ ] **Step 3: 内容を確認する**

Run:
```bash
cat ~/.copilot/copilot-instructions.md
```

Expected output:
```
- 会話・説明・コメントはすべて日本語で応答する
- コード・コマンド・ファイルパス・変数名などは英語のまま維持する
```

- [ ] **Step 4: Copilot CLI で `/instructions` コマンドを実行し、ファイルが認識されていることを確認する**

Copilot CLI 内で実行:
```
/instructions
```

Expected: 一覧に `~/.copilot/copilot-instructions.md` が表示される

- [ ] **Step 5: このリポジトリの既存設定が壊れていないことを確認する**

Run:
```bash
cat /home/tomoya/git/vuln-tools-feed/.github/copilot-instructions.md
```

Expected: 変更なし（英語/日本語 README のルールがそのまま残っている）

```
# Copilot Repository Instructions

- `README.md` MUST be written in English.
- `README_ja.md` MUST be written in Japanese.
```
