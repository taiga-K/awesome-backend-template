## 言語設定
回答は必ず日本語で行ってください

## アーキテクチャ
本プロジェクトではDDD×クリーンアーキテクチャ構成を採用します

## 技術スタック
- 開発言語: Go言語
- Webフレームワーク: Gin
- ログ: slog

## 初回確認ファイル
- 作業開始時は `AGENTS.md` `ARCHITECTURE.md` `CONTRIBUTING.md` `README.md` を先に確認してください
- コードレビューを行う場合は `REVIEW.md` も追加で確認してください

## エージェント利用方針
ユーザーからの指示なしに積極的にサブエージェントを使用してください。
修正対象が被らない並列で作業が可能な場合は、積極的に動的サブエージェントを使用して並列で作業してください。

- ドメイン知識や用語確認が必要な場合は `domain-doc-researcher` を使ってください
- 責務配置やレイヤ境界の判断が必要な場合は `architecture-boundary-reviewer` `domain-designer` `usecase-orchestrator` を使ってください
- TDD で進める変更は `tdd-orchestrator` を起点にしてください
- Go コード変更後は `go-code-reviewer` を使ってください
- コードレビュー時は変更箇所に応じて `domain-code-reviewer` `usecase-code-reviewer` `presentation-code-reviewer` `infra-code-reviewer` `api-contract-reviewer` `security-code-reviewer` を使い分けてください

## 作業フロー
- いきなり実装せず、まず対象レイヤと責務の置き場所を判断してください
- 用語、ユースケース、API 契約、利用方法に影響する変更では、コードと関連文書を同じ変更単位で扱ってください
- TDD で進める場合は、先に観点整理またはテスト項目表を作成し、承認後にテストと実装へ進んでください
- テストは変更内容に応じて選び、固定のカバレッジ数値だけで品質を判断しないでください
