---
name: domain-layer
description: Defines domain-layer guidance for this repository in DDD x Clean Architecture, including domain responsibilities, aggregate boundaries, value objects, repository abstractions, `internal/domain` splitting, `docs/domain` use case and domain model documents, ubiquitous language maintenance, and deriving `docs/api` OpenAPI from domain documents. Expected outputs include concise domain-layer recommendations with reasons, document sync steps, or domain-derived OpenAPI drafts with assumptions and Redocly verification status. Use when designing, implementing, reviewing, or documenting the domain layer, `docs/domain`, or domain-derived APIs in this repository.
---

# ドメイン層

## いつ使うか

- ドメイン層にどこまでロジックを寄せるべきか判断したいとき
- 値オブジェクト、集約、リポジトリ、外部 API との責務分離を整理したいとき
- エンティティ、値オブジェクト、ドメインサービス、ユースケース境界を Go でどう実装するか決めたいとき
- `NewXxx()` と `Reconstruct()` の使い分けや、ORM/DB モデルとの分離を整理したいとき
- `internal/domain` 配下の構成や分割方針を決めたいとき
- `docs/domain/usecase/`, `docs/domain/uml/`, `docs/domain/ubiquitous-language.md` を作成・更新・レビューしたいとき
- `docs/domain` を根拠に `docs/api` の OpenAPI を起こしたいとき
- ドメイン層またはドメイン文書の変更が API 仕様へどう影響するか整理したいとき

## このスキルの対象

- このリポジトリの **DDD x クリーンアーキテクチャにおけるドメイン層**
- 将来作成する `docs/domain/` 配下のユースケース図、ドメインモデル図、ユビキタス言語
- 将来作成する `docs/api/` 配下の OpenAPI 文書のうち、**ドメイン文書から導出する部分**

このスキルは `ARCHITECTURE.md` の保守を扱わない。  
API の path、HTTP メソッド、エラー形式、認証方式などの **Web API 設計判断** は、必要に応じて `../api-design/SKILL.md` を併読する。

## 期待する出力

- ドメイン層の判断では、**結論、理由、置き場所、注意点** を短く分けて返す
- `docs/domain` の整備では、**どの文書を更新すべきか** と **同期が必要な周辺文書** を明示する
- `docs/domain` から OpenAPI を起こすときは、**確定事項、未確定事項、補った仮定、Redocly 検証状況** を分けて返す

## 基本原則

- **重要なビジネスルールはドメイン層に寄せる**
- **What は内側、How は外側に置く**
- **単一集約の不変条件はドメイン、複数集約の調停はまずユースケース層（application層）を疑う**
- **推測で用語、図、API 仕様を増やさない**

詳細な判断基準の正本は `references/domain-core.md` とし、ここでは入口だけを示す。

## 最初に確認する

1. `AGENTS.md`
2. 依頼がコード中心か、文書中心か、API 派生中心かを切り分ける
3. 既存の `docs/domain/` または `docs/api/` があれば読む
4. Web API 設計判断が必要なら `../api-design/SKILL.md` を読む
5. 情報が足りないなら、埋めずにユーザーへ確認する

判断、実装、レビューでは、**該当する論点の `references/*.md` を開いてから** 進める。

## 作業の入口

### 1. ドメイン層の責務を判断したい

- `references/domain-core.md` を読む
- ドメインオブジェクト、リポジトリ、集約、外部連携、命名、削除、再構成の論点を扱う
- このテーマの詳細判断は、原則として `references/domain-core.md` を正本にする

### 1.5. Go の実装パターンまで欲しい

- `references/go-implementation.md` を読む
- `NewXxx()` と `Reconstruct()` の分離、Go の型設計、repository interface、テスト観点を扱う

### 2. `internal/domain` の構成を決めたい

- `references/directory-splitting.md` を読む
- 業務境界での分割、肥大化シグナル、ユースケース層へ上げる判断、具体例を扱う

### 3. `docs/domain` を整備したい

- `references/domain-documents.md` を読む
- ユースケース図、ユビキタス言語、ドメインモデル図の順と相互同期を扱う

### 4. `docs/domain` から `docs/api` を起こしたい

- `references/domain-to-openapi.md` を読む
- その上で API 設計判断が必要なら `../api-design/SKILL.md` を読む
- `docs/api` に成果物を作るなら、必要に応じて `.cursor/commands/openapi.md` の Redocly 手順も確認する

## 判断順序

1. まず、問いが **ドメインの不変条件**、**ユースケースの調停**、**インフラの実装詳細** のどれかを切り分ける
2. ドメインに置くと決めたら、**集約境界** と **依存方向** を先に確認する
3. Go 実装の話なら、**生成時ルール** と **再構成** と **ORM 分離** の 3 点を先に確認する
4. `internal/domain` をいじるなら、**業務境界で追いやすいか** を基準に構成を決める
5. 概念や境界が変わるなら、必要に応じて `docs/domain/usecase/`, `docs/domain/ubiquitous-language.md`, `docs/domain/uml/` を同じ変更単位で更新する
6. `docs/domain` から `docs/api` を起こすなら、**確定事項** と **仮定** を分けて出す
7. `docs/api` に保存する依頼なら、Redocly による lint / bundle の前提ファイルがあるか確認し、検証できたかどうかを結果に含める

## してはいけないこと

- 集約横断の手順や副作用の調停を安易にドメイン層へ押し込むこと
- `internal/domain/model` と `internal/domain/service` を最初からトップレベルに置くこと
- `shared`, `common`, `util` を安易な退避場所にすること
- `domain` struct に ORM tag や HTTP/JSON 都合を直接書くこと
- ORM の entity や DB row をそのままドメインオブジェクトとして使い回すこと
- setter 連打で不変条件を外から壊せるようにすること
- 集約の一部だけを更新する convenience API を安易に公開すること
- `TaskService` `OrderService` のような責務が曖昧な命名へ逃げること
- 実装詳細や API パラメータ一覧をユビキタス言語へ持ち込むこと
- ドメインモデル図やユースケース図から、未確認の API 設計を確定事項として書くこと
- 依頼がない限り PNG、SVG、PDF などの画像成果物を追加すること
- `docs/api` に保存する依頼で、単一ファイル YAML のまま完了扱いにすること
- Redocly 前提の検証が必要なのに、`redocly.yaml` や `docs/api/openapi.yaml` の不足を無視して「検証済み」と扱うこと

## 追加資料

- ドメイン層の責務、値オブジェクト、リポジトリ、集約、命名: [references/domain-core.md](references/domain-core.md)
- Go でのエンティティ、値オブジェクト、再構成、repository interface: [references/go-implementation.md](references/go-implementation.md)
- `internal/domain` の分割と肥大化判断: [references/directory-splitting.md](references/directory-splitting.md)
- `docs/domain` のユースケース図、ユビキタス言語、ドメインモデル図: [references/domain-documents.md](references/domain-documents.md)
- `docs/domain` から `docs/api` へ落とす手順: [references/domain-to-openapi.md](references/domain-to-openapi.md)
- 具体例: [examples.md](examples.md)
