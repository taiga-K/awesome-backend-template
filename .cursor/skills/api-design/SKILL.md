---
name: api-design
description: Defines Web API design rules for this repository, including endpoint naming, HTTP methods, query parameters, response and error formats, versioning, security, caching, and rate limiting. Use when designing or reviewing API contracts, endpoint structures, OpenAPI conventions, or API consistency in this repository.
---

# API 設計

## いつ使うか

- API の path / HTTP メソッド / versioning を決めるとき
- OpenAPI の設計方針を決めるとき
- レスポンス形式、エラー形式、認証方式、キャッシュ方針を揃えるとき
- 既存 API のレビューや規約確認をするとき

## 基本方針

- **仕様があるものは仕様に従う。ないものはデファクトスタンダードに従う**
- **使いやすさ・変更しやすさ・頑強さを優先する**
- **内部実装ではなく、利用者のユースケースから API を設計する**
- **HTTP の仕様を最大限利用し、不要な独自ルールを増やさない**
- **後方互換性を重視し、破壊的変更は最小限にする**

## 設計の進め方

1. 対象利用者、対象画面、対象操作、対象クライアントを確認する
2. ユースケースから公開する機能を決める
3. リソース、URI、HTTP メソッド、クエリパラメータを決める
4. レスポンス形式、エラー形式、ステータスコードを決める
5. 認証、セキュリティ、レートリミット、キャッシュ、バージョニングを決める
6. **設計後に Web API チェックリストで確認する**
7. OpenAPI へ落とす

## 追加資料

- 原則と利用者別設計: [references/principles.md](references/principles.md)
- エンドポイント設計: [references/endpoint-design.md](references/endpoint-design.md)
- レスポンスとエラー: [references/response-and-errors.md](references/response-and-errors.md)
- バージョニングと運用・セキュリティ: [references/versioning-security.md](references/versioning-security.md)
- 設計後チェックリスト: [references/web-api-checklist.md](references/web-api-checklist.md)
- 例: [examples.md](examples.md)
