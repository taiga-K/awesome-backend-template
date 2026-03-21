---
name: push-branch
description: 現在のブランチを origin に push し、必要なら upstream を設定する。ユーザーが push・リモート反映・origin へ送ることを依頼したとき、PR 作成前にリモートへブランチを載せる必要があるとき、create-commit 後に共有リポジトリへ反映するときに使用する。GitFlow の feature/release/hotfix ブランチの共有に使う。
---

# push-branch

ローカルコミットをリモート `origin` へ送る。初回は追跡ブランチ（upstream）を設定し、2 回目以降は通常の `git push` で同期する。

## いつ使うか

- ユーザーが「push して」「リモートに上げて」「origin に反映」と依頼したとき
- `gh pr create` や PR レビューの前に、ブランチをリモートに存在させる必要があるとき
- `create-commit` 後に、チームと共有するために送るとき

## 事前確認

1. **未コミットの意図しない変更がないか**

   ```bash
   git status --porcelain
   ```

   - 送りたくない変更が残っていれば、コミット・stash・破棄のどれにするかユーザーに確認する

2. **リモートとブランチ名**

   - 既定は `origin`。別名のリモートを使う場合はユーザー指示に従う
   - 現在ブランチ名は `git branch --show-current` または `git status` で確認できる

## 基本フロー

### 初回（upstream 未設定）

現在ブランチを `origin` に載せ、以降の `git push` / `git pull` の基準を揃える。

```bash
git push -u origin HEAD
```

ブランチ名を明示する場合:

```bash
git push -u origin <ブランチ名>
```

### 2 回目以降（upstream 済み）

```bash
git push
```

追跡が設定されているかは次で確認できる。

```bash
git branch -vv
```

## GitFlow との対応

| ブランチ例 | 想定 |
|-----------|------|
| `feature/*` | develop 向け PR 前に `origin` へ push |
| `release/*` | リリース作業の共有・PR 前に push |
| `hotfix/*` | 緊急修正の共有・PR 前に push |
| `main` / `develop` | 保護ブランチの場合はリポジトリルールに従う（直接 push が禁止のことが多い） |

## 安全に関する注意

- **`git push --force` は使わない**（ユーザーが明示的に要求し、共有ブランチでない・履歴書き換えが合意されている場合のみ検討）
- 履歴の上書きが必要でユーザーが明示した場合は、**`--force-with-lease`** を優先し、対象ブランチとリスクを短く説明してから実行する
- 機密情報を含むコミットが混ざっていないか、必要なら `git log` / diff で確認してから push する

## よくあるオプション

| 状況 | 例 |
|------|-----|
| タグもまとめて送る | `git push origin --tags`（ユーザー依頼時のみ） |
| 複数リモート | ユーザーが指定したリモート名を使う |

## 出力例

**状況**: `feature/add-login` を初めて `origin` に載せる

```bash
git status --porcelain
git push -u origin HEAD
```

**状況**: 既に upstream がある

```bash
git push
```
