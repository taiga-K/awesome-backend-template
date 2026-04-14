---
name: review-md-update
description: Updates `REVIEW.md` for this repository's backend API code review policy. Use when the user asks to create, revise, refine, reorganize, or maintain `REVIEW.md`, review guidelines, reviewer guidance, or code review policy for this repository.
---

# REVIEW.md 更新

このスキルは、このリポジトリの `REVIEW.md` を作成または更新するときに使う。

目的は、テンプレート由来の一般論をそのまま転記せず、このリポジトリの `DDD x クリーンアーキテクチャ`、Go 実装方針、バックエンド API 前提に合わせて、実務で使えるコードレビューガイドラインへ整えることです。

## まず確認する

1. `AGENTS.md`
2. 既存の `REVIEW.md`
3. `ARCHITECTURE.md`
4. `CONTRIBUTING.md`
5. `.github/PULL_REQUEST_TEMPLATE.md`
6. `.cursor/skills/go-implementation/SKILL.md`
7. `.cursor/skills/domain-layer/SKILL.md`
8. `.cursor/skills/usecase-layer/SKILL.md`
9. `.cursor/skills/presentation-layer/SKILL.md`
10. `.cursor/skills/infra-layer/SKILL.md`
11. `.cursor/skills/security-rules/SKILL.md`

必要に応じて `docs/domain` と `docs/api` も参照してよい。

## この文書で維持すること

- 実務エンジニアがすぐに使える具体性
- 日本語、ですます調
- Markdown の見出し構造
- バックエンド API リポジトリとしての前提
- DDD x クリーンアーキテクチャの責務境界
- Go のレビュー観点
- セキュリティレビュー観点

## 書き方の原則

- 方針、考え方、運用ルール、補足説明は自然文で書く
- 箇条書きはチェックリスト、判断基準、列挙が本質な項目に限定する
- 箇条書きが 2 項目程度なら、可能な限り文章へ統合する
- 抽象的な精神論より、レビュアーが次に何を見るか分かる表現を優先する
- テンプレートの見出しを流用するときも、不要な章は残さず削る
- テンプレートの表現がこのリポジトリに合わないときは、名称ごと置き換える

## このリポジトリ向けの固定方針

- リポジトリ名は、明示的に求められない限り本文やタイトルへ書かない
- `REVIEW.md` のタイトルは一般化したものを使う
- 本リポジトリはバックエンド API 開発前提なので、UI 前提の章はそのまま残さない
- UI 変更確認の話題が必要なら、`API変更の確認` として API 契約、実測、認証認可、後方互換性へ置き換える
- 分散チーム、タイムゾーン、UI デザイナーのように現状不要な運用項目は、要求がない限り追加しない
- CL サイズでは、レビューしやすさを述べてもよいが、分割方針を勝手に強く書かない
- `domain`、`usecase`、`presentation`、`infra` の責務境界をレビュー基準へ必ず反映する
- `README.md`、`docs/domain`、`docs/api` との整合性確認をドキュメント要件へ反映する
- セキュリティ観点を追加する場合は、`.cursor/skills/security-rules/SKILL.md` を参照し、関連する `rule_id` と `references/*.md` を根拠にする
- `REVIEW.md` ではセキュリティルールへの参照は書いてよいが、サブエージェントの存在や使い方には触れない

## 更新手順

1. 既存の `REVIEW.md` を読み、残す内容と直す内容を分ける
2. 外部テンプレートやユーザー指示がある場合は、見出し構造を保ちながら本リポジトリ向けに言い換える
3. `ARCHITECTURE.md` と各レイヤースキルから、レビューで守るべき責務境界を抽出する
4. Go 実装・レビュー観点から、命名、エラー処理、制御フロー、依存方向、テスト観点を反映する
5. セキュリティ観点が関わる場合は `.cursor/skills/security-rules/SKILL.md` を読み、`REVIEW.md` に反映すべきレビュー基準だけを抽出する
6. バックエンド API に不要な章は削除し、必要なら API 向け表現へ置き換える
7. 参照情報が必要なら、関連資料への Markdown リンクを `REVIEW.md` に追加する
8. 更新後に全体を読み返し、見出し番号、表現の重複、テンプレートの残骸、サブエージェントへの言及がないか確認する
9. 可能なら `REVIEW.md` の lint を確認する

## よくある置き換え

- `UI変更の確認` は `API変更の確認` へ置き換える
- リポジトリ固有名を含むタイトルは一般化する
- 分散チーム前提の節は削除する
- 汎用的すぎる承認基準は、レイヤー境界と文書同期を含む基準へ寄せる
- セキュリティの補助導線が必要なら、`.cursor/skills/security-rules/SKILL.md` への参照へ置き換える

## 迷ったとき

- このリポジトリに本当に必要な運用かを先に確認する
- 一般論を足すか迷ったら、既存の設計資料に根拠がある内容だけを書く
- 箇条書きが増えすぎたら、運用説明を自然文へ戻す
- セクション名がずれているなら、無理に残さず目的に合う名前へ変える
- セキュリティ観点を足すか迷ったら、`security-rules` に根拠がある内容だけを書く

## 仕上げ

- 不要なテンプレート文言、絵文字、区切り線を消す
- リポジトリ名の取りこぼしがないか確認する
- API リポジトリ前提と矛盾する記述がないか確認する
- セキュリティ導線がある場合、`security-rules` 参照に統一し、サブエージェントへの言及が混ざっていないか確認する
- レビュー担当者がそのまま運用に使える密度になっているか確認する
