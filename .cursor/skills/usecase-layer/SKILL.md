---
name: usecase-layer
description: Defines usecase-layer guidance for this repository in DDD x Clean Architecture, including usecase responsibilities, orchestration, transaction boundaries, DTOs, repository and external service ports, `internal/usecase` splitting, and `docs/domain/usecase` maintenance. Expected outputs include concise usecase-layer recommendations with reasons, placement guidance, transaction and side-effect handling notes, or small Go-oriented usecase templates with assumptions. Use when designing, implementing, reviewing, or documenting the usecase layer in this repository.
---

# ユースケース層

## いつ使うか

- ユースケース層に何を置き、何を置かないか判断したいとき
- 単一集約のルールと、複数集約の調停を切り分けたいとき
- トランザクション境界、外部 API 呼び出し、通知送信の責務を整理したいとき
- `internal/usecase` の構成を決めたいとき
- Input/Output DTO の置き方や戻り値の設計を決めたいとき
- `docs/domain/usecase/` の文書を作成・更新・レビューしたいとき
- ドメイン層、インフラ層、プレゼンテーション層の間で何を仲介するか整理したいとき

## このスキルの対象

- このリポジトリの **DDD x クリーンアーキテクチャにおけるユースケース層**
- 将来作成する `docs/domain/usecase/` 配下のユースケース記述
- ユースケース層から見たトランザクション、外部連携、副作用順序の設計

このスキルは、単一集約の不変条件そのものを定義しない。  
その判断が必要なら `../domain-layer/SKILL.md` を併読する。

## 期待する出力

- ユースケース層の判断では、**結論、理由、置き場所、注意点** を短く分けて返す
- 実装相談では、**どこまでをユースケース層に残すか** を最初に明示する
- トランザクションや副作用が絡む場合は、**同期処理、非同期化候補、失敗時の扱い** を分けて返す

## 基本原則

- **ユースケース層は調停役であり、業務知識の本体ではない**
- **単一集約の不変条件はまずドメイン層を疑う**
- **複数集約、外部依存、副作用順序、認可、入出力変換はユースケース層が担う**
- **複数集約はまずユースケース層で調停し、それでもドメイン知識が残るならドメインサービスやイベントも検討する**
- **What は domain、How の流れと順序は usecase**
- **DTO はユースケース境界のために使い、外側の都合をそのまま持ち込まない**
- **ユースケースからユースケースを安易に呼ばない**
- **トランザクション開始位置はユースケース層を第一候補にする**
- **通知、メール、ジョブ投入、外部 API 呼び出しは順序と失敗方針を明示する**
- **ユースケース層を巨大な手続きの置き場にしない**

## 最初に確認する

1. これは単一集約の不変条件か、複数集約の調停か
2. 外部依存の呼び分けや副作用順序があるか
3. トランザクション境界をどこで張るべきか
4. Input/Output DTO が必要か、それとも domain object を返してよいか
5. `docs/domain/usecase/` など同期すべき文書があるか

判断、実装、レビューでは、**該当する論点の `references/*.md` を開いてから** 進める。

## 作業の入口

### 1. ユースケース層の責務を判断したい

- `references/usecase-core.md` を読む
- 調停、DTO、認可、トランザクション、外部依存の境界を扱う

### 2. Go の実装パターンまで欲しい

- `references/go-implementation.md` を読む
- `Run()` の形、Input/Output DTO、port interface、戻り値設計、エラー返却を扱う

### 3. `internal/usecase` の構成を決めたい

- `references/directory-splitting.md` を読む
- ユースケース単位の分割、肥大化シグナル、共通化しすぎない判断を扱う

### 4. トランザクションや副作用を整理したい

- `references/transactions-and-side-effects.md` を読む
- DB 更新、外部 API、通知、非同期化、失敗時リカバリを扱う

### 5. `docs/domain/usecase` を整備したい

- `references/usecase-documents.md` を読む
- ユースケース文書に書く範囲と、ドメイン文書・API 文書との同期範囲を扱う

## 判断順序

1. まず問いが **ドメインの不変条件** か **ユースケースの調停** かを切り分ける
2. ユースケース層に置くと決めたら、入力、認可、トランザクション、出力の順で責務を確認する
3. 複数集約にまたがる処理なら、まずユースケース層で調停し、そこにドメイン知識が残り続けるならドメインサービスやイベントを検討する
4. 複数集約にまたがる処理では、どこまでを同期で完了させるか決める
5. 外部 API や通知があるなら、失敗時の扱いと再実行方針を確認する
6. ディレクトリ構成を決めるときは、共通化よりユースケースごとの追いやすさを優先する
7. 概念や流れが変わるなら、必要に応じて `docs/domain/usecase/` を同じ変更単位で更新する

## してはいけないこと

- 単一集約の検証や状態遷移を、何でもユースケース層に押し込むこと
- ユースケースから別ユースケースを安易に直接呼ぶこと
- HTTP request/response の都合をそのまま Input/Output DTO に持ち込むこと
- `UsecaseService`, `ApplicationService` のような曖昧な巨大クラスへ逃げること
- トランザクションと外部 API 呼び出しの順序を曖昧にしたまま実装すること
- 副作用の失敗方針を決めずに「とりあえず同期実行」にすること
- `shared`, `common`, `util` にユースケース共通処理を雑に寄せること

## 追加資料

- ユースケース層の責務、DTO、調停、認可、戻り値: [references/usecase-core.md](references/usecase-core.md)
- Go での Input/Output DTO、port、`Run()` の形: [references/go-implementation.md](references/go-implementation.md)
- `internal/usecase` の分割と肥大化判断: [references/directory-splitting.md](references/directory-splitting.md)
- トランザクション境界と副作用順序: [references/transactions-and-side-effects.md](references/transactions-and-side-effects.md)
- `docs/domain/usecase` の記述と同期範囲: [references/usecase-documents.md](references/usecase-documents.md)
- 具体例: [examples.md](examples.md)
