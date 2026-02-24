---
name: create-branch
description: Create Git branches following GitFlow strategy. Use when creating a new branch, switching to a feature/release/hotfix branch, or when the user asks to make a branch. Supports feature, release, and hotfix branch types with correct parent selection.
---

# create-branch

GitFlow に従い、適切な親ブランチから適切な命名でブランチを作成する。

## ブランチ種類の判断

1. ブランチの種類を特定する：

   | 種類 | 用途 | 親ブランチ | 命名形式 |
   |------|------|------------|----------|
   | **feature** | 新機能開発 | develop | `feature/<名前>` |
   | **release** | リリース準備 | develop | `release/<バージョン>` |
   | **hotfix** | 本番の緊急修正 | main | `hotfix/<名前>` |

2. 該当する種類に従い、親ブランチと命名規則で作成する。

## 命名規則

| 種類 | 例 |
|------|------|
| feature | `feature/add-user-auth`, `feature/issue-123-login` |
| release | `release/1.2.0`, `release/v2.0.0` |
| hotfix | `hotfix/fix-payment-crash`, `hotfix/issue-456-null-check` |

- 小文字とハイフンを使用
- 簡潔で内容が分かる名前にする

## 作成コマンド

### feature ブランチ

```bash
git fetch origin develop
git checkout develop
git pull origin develop
git checkout -b feature/<ブランチ名>
```

### release ブランチ

```bash
git fetch origin develop
git checkout develop
git pull origin develop
git checkout -b release/<バージョン>
```

### hotfix ブランチ

```bash
git fetch origin main
git checkout main
git pull origin main
git checkout -b hotfix/<ブランチ名>
```

## 親ブランチの扱い

- `main` が存在しない場合は `master` を使用する
- リモートに `origin/develop` がない場合は、ローカルの develop から作成してもよい（新規リポジトリなど）
- ユーザーが明示的に別の親を指定した場合は従う

## 出力例

**入力**（ユーザーの意図）: ログイン機能を開発する

**実行**:
```bash
git fetch origin develop
git checkout develop
git pull origin develop
git checkout -b feature/add-login
```

**入力**: バージョン 1.2.0 のリリース準備

**実行**:
```bash
git fetch origin develop
git checkout develop
git pull origin develop
git checkout -b release/1.2.0
```

**入力**: 本番の決済エラーを緊急修正

**実行**:
```bash
git fetch origin main
git checkout main
git pull origin main
git checkout -b hotfix/fix-payment-error
```

## 補足

- 作成前に `git status` で作業ツリーがクリーンか確認する。未コミット変更があればユーザーに確認
- リモートに push する指示がなければ、ローカル作成のみでよい
