---
name: infra-layer
description: Defines infrastructure-layer guidance for this repository in DDD x Clean Architecture, including repository implementations, ORM and SQL isolation, persistence mapping, transaction manager placement, external client adapters, optimistic locking, `internal/infra` splitting, and testing boundaries. Expected outputs include concise infrastructure-layer recommendations with reasons, placement guidance, mapping and locking notes, or small Go-oriented repository and client templates with assumptions. Use when designing, implementing, reviewing, or documenting the infrastructure layer in this repository.
---

# インフラ層

## いつ使うか

- インフラ層に何を置き、何を置かないか判断したいとき
- repository の実装を Go でどう書くか決めたいとき
- ORM、SQL、DB row、query builder をどこまで閉じ込めるか整理したいとき
- Redis、Slack、メール、HTTP client など外部接続をどこに置くか決めたいとき
- transaction manager、排他制御、楽観ロックの責務を整理したいとき
- `internal/infra` の分割方針を決めたいとき
- インフラ層のテストをどう切るか決めたいとき

## このスキルの対象

- このリポジトリの **DDD x クリーンアーキテクチャにおけるインフラ層**
- repository 実装、外部 API client 実装、transaction manager 実装
- `internal/infra` 配下のディレクトリ分割

このスキルは、repository interface や外部 client interface をどの層に置くかの判断は扱うが、  
単一集約の不変条件やユースケースの調停そのものは扱わない。必要なら `../domain-layer/SKILL.md` と `../usecase-layer/SKILL.md` を併読する。

## 期待する出力

- インフラ層の判断では、**結論、理由、置き場所、注意点** を短く分けて返す
- 実装相談では、**domain から隔離すべき実装詳細** を最初に明示する
- 永続化や外部接続が絡む場合は、**マッピング、排他制御、失敗時の扱い、テスト方針** を分けて返す

## 基本原則

- **インフラ層は実装詳細を閉じ込める層であり、業務ルールの本体ではない**
- **ORM、SQL、DB row、SDK、HTTP client はインフラ層に閉じ込める**
- **repository interface は domain、実装は infra に置く**
- **DB の値から domain object を再構成する責務は repository 実装が担う**
- **OR マッパークラスを domain や usecase に漏らさない**
- **集約単位で永続化する**
- **楽観ロックやページング、ロック取得などの永続化詳細は infra 側で実現する**
- **保存後の domain event 発行や outbox 連携は、repository 実装責務として検討する**
- **Slack やメールなど実現方法の詳細は infra に閉じ込める**
- **rollback 特性が異なる外部接続は、`Repository` と `Client` や `Storage` を安易に混同しない**
- **集約単位の repository では重すぎる read 要件は、query model や軽量 CQRS を逃がし先にする**
- **transaction manager は usecase から使われる前提で infra 実装を提供する**
- **domain をテストしやすくするために、infra の都合を内側へ逆流させない**

## 最初に確認する

1. これは domain interface の実装か、usecase 用 port の実装か
2. 何を隔離したいのか: ORM、SQL、DB、Redis、外部 API、SDK
3. 集約単位の保存と取得になっているか
4. DB row から domain object への再構成が必要か
5. 排他制御、transaction、リトライが必要か
6. 保存後に domain event 発行や outbox 連携が必要か
7. read 側は repository で十分か、query model が必要か

判断、実装、レビューでは、**該当する論点の `references/*.md` を開いてから** 進める。

## 作業の入口

### 1. インフラ層の責務を判断したい

- `references/infra-core.md` を読む
- repository 実装、ORM/SQL 隔離、再構成、interface の置き方を扱う

### 2. Go の実装パターンまで欲しい

- `references/go-implementation.md` を読む
- repository 実装、transaction manager、client adapter の最小形を扱う

### 3. `internal/infra` の構成を決めたい

- `references/directory-splitting.md` を読む
- 技術要素単位と repository/client 分割、肥大化シグナルを扱う

### 4. 永続化・排他制御・外部クライアントを整理したい

- `references/persistence-and-clients.md` を読む
- OR マッパー、再構成、optimistic lock、通知 client、event 発行、認証情報の実装位置を扱う

## 判断順序

1. まず問いが **domain の責務** か **infra の実装詳細** かを切り分ける
2. infra に置くと決めたら、domain interface と実装詳細の境界を確認する
3. 永続化なら、集約単位、再構成、排他制御、transaction 依存の順で確認する
4. 保存後に domain event を流すなら、repository 実装または outbox の責務としてどこに置くか決める
5. 外部 API なら、domain/usecase が知るべき抽象と、infra に閉じ込める実装詳細を分ける
6. rollback 特性が異なる接続は、`Repository` / `Client` / `Storage` の命名を分ける
7. read 側が重いなら、query model や `query_service` を使うかを判断する
8. ディレクトリ構成を決めるときは、技術要素ごとの追いやすさと repository/client の見通しを優先する
9. テストでは unit と integration の境界を先に明示する

## してはいけないこと

- OR マッパークラスや DB row を domain object として使い回すこと
- `gorm` tag や SQL 都合を domain へ持ち込むこと
- repository 実装に業務ルールの本体を書き始めること
- 集約の一部だけを都合よく更新する API を乱立させること
- rollback 特性が違う処理を、同じ `Repository` 抽象に雑に押し込むこと
- Slack SDK や HTTP client の詳細を usecase や domain に漏らすこと
- transaction と外部 API 呼び出しの責務を repository 実装へ押し込み過ぎること
- read 性能の問題を全部 repository だけで解こうとして、query model の選択肢を封じること
- `shared`, `common`, `util` に何でも逃がすこと

## 追加資料

- インフラ層の責務、repository 実装、再構成、interface 境界: [references/infra-core.md](references/infra-core.md)
- Go での repository 実装、client adapter、transaction manager: [references/go-implementation.md](references/go-implementation.md)
- `internal/infra` の分割と肥大化判断: [references/directory-splitting.md](references/directory-splitting.md)
- OR マッパー、楽観ロック、外部 client 実装: [references/persistence-and-clients.md](references/persistence-and-clients.md)
- 具体例: [examples.md](examples.md)
