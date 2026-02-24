---
name: create-commit
description: Conventional Commits（スコープ必須、件名・本文は日本語）形式でコミットメッセージを生成します。コミット作成やコミットメッセージ執筆、ユーザーからコミット作成要請があった場合に使用します。git diffを解析して、論理的な最小単位でコミットを行います。
---

# create-commit

過去のcommitとの差分を取得し、変更内容を把握した上で、論理的に変更最小単位でcommitを実行する。

## 手順

### 1. 変更差分を取得

```bash
git status --porcelain
```

- 未追跡ファイル（`??`）があれば `git add` でステージング
- `git diff --cached` でステージング済みの差分を取得
- 未ステージの変更は `git diff` で確認

### 2. 変更内容を把握

- 差分を分析し、変更の種類（追加・修正・削除）を確認
- 関連するファイル群を特定する

### 3. 論理的に変更最小単位でcommit

- 1つのcommitには1つの明確な目的
- 複数の変更は `git add` でステージングを分けて実行
- **未追跡ファイルを含む変更されたファイルはすべてcommitする**

## Conventional Commits 形式

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

| 要素 | ルール |
|------|--------|
| type | 小文字。`build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test` から選択 |
| scope | **必須**。対象領域を明確にする |
| subject | 簡潔に（50字推奨）。ヘッダー全体は100字以内。末尾に句点・ピリオドを付けない |
| body（本文） | **必須**（日本語）。ヘッダーとの間に空行。1行100字以内で適宜改行 |
| footer | あれば body との間に空行。各行100字以内 |

## 出力例

**入力**（変更内容）: ユーザー認証に JWT を追加

**出力**:
```
feat(auth): JWT によるユーザー認証を実装

ログインエンドポイントとトークン検証ミドルウェアを追加
```

**入力**: 日付表示のバグ修正

**出力**:
```
fix(reports): タイムゾーン変換時の日付フォーマットを修正

レポート生成で UTC タイムスタンプを一貫して使用
```

## commit実行コマンド

**zsh の場合**（推奨、複数行 body を保持）:
```bash
git commit -F =(cat <<'MSG'
type(scope): subject

本文1行目（100字以内で改行）
本文2行目
本文3行目

refs: #123
MSG
)
```

**bash の場合**（複数 `-m` で段落区切り）:
```bash
git commit -m "type(scope): subject" -m "本文1行目" -m "本文2行目"
```

## 複数変更を分割してcommitする場合

```bash
git status --porcelain

# 1つ目
git add <ファイル1>
git commit -F =(cat <<'MSG'
type(scope1): subject1

body1-1行目（100字以内で改行）
body1-2行目
MSG
)

# 2つ目
git add <ファイル2>
git commit -F =(cat <<'MSG'
type(scope2): subject2

body2-1行目（100字以内で改行）
body2-2行目
MSG
)
```

## 必須事項

- subject と body（本文）は**日本語**で記述
- ヘッダー（`<type>(<scope>): <subject>`）は100字以内
- body（本文）/ footer は各行100字以内

## 補足

- ステージング済みの変更がない場合は commit を実行しない
- `--amend` の指示がある場合は従う
