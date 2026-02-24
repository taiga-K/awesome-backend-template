---
name: create-commit
description: Conventional Commits（スコープ必須、件名・本文は日本語）形式でコミットメッセージを生成します。コミット作成やコミットメッセージ執筆、ユーザーからコミット作成要請があった場合に使用します。git diffを解析して、論理的な最小単位でコミットを行います。
---

# create-commit

このスキル適用時は、必ず以下のファイルの内容を参照して実行する。

## 必須

**参照ファイル**: `.agents/skills/create-commit/SKILL.md`

実行開始時に上記ファイルを Read ツールで読み込み、記載の手順・Conventional Commits 形式・ルールに従って commit を実行する。
