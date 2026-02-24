---
name: fetch-github-issues
description: Fetch GitHub issues using gh CLI. Lists 10 oldest issues when no number specified; fetches a specific issue when a number or URL is given. Use when the user asks to get issues, list issues, fetch an issue, or view issue details.
---

# GitHub Issue 取得

gh コマンドで issue を取得する。指定なしなら古い順に10件を一覧、指定ありならその issue の詳細を取得。

## 前提条件

- GitHub CLI (`gh`) がインストール済み
- リポジトリで認証済み (`gh auth status`)

## 使い分け

| ユーザーの指定 | 実行するコマンド |
|----------------|------------------|
| 何も指定なし | 古い順に10件一覧 |
| issue番号（例: 3） | その issue の詳細 |
| issue URL | その issue の詳細 |

## 一覧取得（指定なし）

古い順（作成日昇順）に10件を表示:

```bash
gh issue list --state all --limit 10 --search "sort:created-asc"
```

別リポジトリの場合:

```bash
gh issue list -R owner/repo --state all --limit 10 --search "sort:created-asc"
```

## 詳細取得（番号・URL指定）

```bash
gh issue view <number>
# または
gh issue view <url>
```

コメントも含める場合:

```bash
gh issue view <number> --comments
```

## 出力例

**一覧**（タブ区切り）:
```
#	TITLE	STATE	LABELS	CREATED
1	初期セットアップ	CLOSED	enhancement	2026-02-16T05:41:17Z
2	Dockerfile作成	OPEN	infra	2026-02-15T15:58:07Z
...
```

**詳細**: タイトル、本文、ラベル、作成日等を表示。
