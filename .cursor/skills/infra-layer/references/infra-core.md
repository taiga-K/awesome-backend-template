# インフラ層の責務

## いつ使うか

- repository 実装をどこまで担うか迷ったとき
- ORM や SQL をどの層へ閉じ込めるか整理したいとき
- domain object の再構成責務を確認したいとき

## 基本方針

- インフラ層は永続化や外部接続の **実現方法** を引き受ける
- domain は抽象と業務知識、infra は実装詳細を担当する
- repository interface は domain、実装クラスは infra に置く

## repository 実装の責務

- domain object を DB 保存用の値へ詰め替える
- DB から取得した値を domain object へ再構成する
- ORM、SQL、query builder、driver の詳細を隠蔽する
- 集約単位で保存・取得する
- ロック、ページング、悲観ロック、楽観ロックなど永続化都合を実現する
- 保存後に必要な domain event 発行や outbox 連携を担うことがある

## インフラ層に置くもの

- repository 実装
- transaction manager 実装
- DB client、Redis client
- 外部 API client 実装
- ORM model、DB row、generated query code

## インフラ層に置かないもの

- 集約の不変条件
- 単一集約の状態遷移ルール
- usecase の手順そのもの
- HTTP request/response 変換の本体

## 再構成

- 新規生成と再構成は別経路で扱う
- repository 実装は DB から取得した値を `Reconstruct()` 系へ渡して domain object を返す
- domain object の生成ルールを repository から勝手に書き換えない

## `save` / `upsert` の扱い

- `save` 1 本で insert/update を隠すと、呼び出し側は簡潔になる
- その一方で、repository 実装内の分岐や責務が増えやすい
- 新規保存か更新かが usecase 側で明確なら、分けた方が低凝集になりにくい
- どちらを選ぶかは、呼び出し側の単純さと repository の責務増加を比較して決める

## ORM の扱い

- OR マッパークラスは repository 実装の中でだけ使う
- domain や usecase に OR マッパーを漏らさない
- OR マッパー都合のフィールド追加を domain に直結させない

## read model / query service

- read 性能や検索要件のために、集約を毎回フル再構成すると重いことがある
- その場合、read 側は `query_service` や query model へ逃がしてよい
- ただし、更新系の整合性ルールまで read model 側へ持ち込まない
- 「集約の一貫性を守る update」と「高速に読む query」を分ける意図を明確にする

## 命名と rollback 特性

- rollback 可能な DB 永続化と、不可逆な外部送信は同じ粒度で扱わない
- その違いが重要なら `Repository` ではなく `Client`, `Gateway`, `Storage` などを使い分ける
- 命名は実現方式ではなく、transaction 上の性質も反映させる

## テスト方針

- domain の unit test と infra の test を分ける
- infra 側では mapping、query、transaction、ロックの動きを確認する
- OR マッパーの挙動に依存するテストは infra に閉じる

## 回答の出し方

1. 結論
2. domain との境界
3. infra の責務
4. 注意点
