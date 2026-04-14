---
name: deslop
description: Reviews diffs against the main branch and removes AI-generated code slop while preserving behavior. Use when cleaning up generated code, simplifying overly defensive or noisy changes, removing unnecessary comments, casts to any, awkward nesting, or other patterns inconsistent with the surrounding codebase.
---

# Remove AI Code Slop

`main` との差分を確認し、ブランチに入り込んだ AI 生成由来のノイズを取り除く。

## Focus Areas

- ローカルのスタイルと比べて不要、または浮いているコメント
- 信頼されたコードパスでは過剰な防御チェックや `try/catch`
- 型問題をごまかすためだけに使われている `any` キャスト
- 早期 return で簡潔にできるのに深くネストしている処理
- そのファイルや周辺コードベースと不整合な、その他の不自然なパターン

## Workflow

1. 現在のブランチと `main` の差分を確認する
2. 生成っぽいコード、ノイズの多いコード、周辺と不整合なコードを特定する
3. ローカルのスタイルと読みやすさを取り戻す最小修正を選ぶ
4. 明確なバグ修正でない限り、挙動は変えない
5. 最後の要約は 1〜3 文で簡潔にまとめる

## Guardrails

- 明確なバグ修正でない限り、挙動を変えない
- 広い書き換えより、最小で焦点の絞られた修正を優先する
- 周辺ファイルとリポジトリ全体のスタイルに合わせる
- 意図や制約を説明する重要なコメントは削除しない
- 最後の要約は 1〜3 文で簡潔にする
