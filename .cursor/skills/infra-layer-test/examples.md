# 例

## 例1: repository 実装 `ProductRepository`

前提:

- `ProductRepository` は `Save`, `FindByID`, 必要なら一覧取得を提供する
- `Save` は domain object を DB 保存用パラメータへ変換する
- `FindByID` は DB row から domain object を再構成する

項目表:

| No | テスト種別 | 対象 | 観点 | 事前状態/入力 | 実行 | 期待結果 | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | `unit` | `ProductRepository` | `repository mapping` | 正常な `Product` | `Save` | query へ正しい保存パラメータが渡る | 基本ケース |
| 2 | `unit` | `ProductRepository` | `domain 再構成` | 正常な `ProductRow` | `FindByID` | `domain.Product` を返す | 基本ケース |
| 3 | `unit` | `ProductRepository` | `domain 再構成` | 不正な row 値 | `FindByID` | 復元失敗を返す | infra で再構成経路を確認する例 |
| 4 | `integration` | `ProductRepository` | `永続化動作` | DB 接続済み | `Save -> FindByID` | 保存した値を取得できる | 実 DB 確認 |
| 5 | `integration` | `ProductRepository` | `query 条件` | 複数件のデータ | 一覧取得 | sort / paging が期待どおり | 必要な場合だけ |
| 6 | `integration` | `ProductRepository` | `transaction 実装` | transaction 内で保存後に失敗 | `tx.Do` | rollback される | tx manager 連携 |
| 7 | `integration` | `ProductRepository` | `排他制御 / version` | version 競合あり | 更新処理 | 競合エラーになる | 楽観ロックがある場合 |
| 8 | `integration` | `ProductRepository` | `回帰` | 過去に null 値で壊れた row | `FindByID` | 再発しない | 再現ケース |

補足:

- この例では `event / outbox 連携` を省略している。保存後 event 処理がある場合だけ追加する
- row 値不正のケースは、domain の業務ルール本体を再検証する意図ではなく、repository の再構成経路が失敗を正しく返すかを見る

## 例2: 外部 client `SlackClient`

前提:

- `SlackClient` は通知用の抽象入力を Webhook request へ変換する
- retry や timeout は adapter の責務として扱う

項目表:

| No | テスト種別 | 対象 | 観点 | 事前状態/入力 | 実行 | 期待結果 | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | `unit` | `SlackClient` | `外部 client request 変換` | 通常の通知入力 | `Notify` | 正しい payload, header, endpoint になる | 基本ケース |
| 2 | `unit` | `SlackClient` | `外部 client response / error 変換` | 200 response | `Notify` | 成功扱いになる | 正常系 |
| 3 | `unit` | `SlackClient` | `外部 client response / error 変換` | 400/500 response | `Notify` | 内側向け error へ変換する | 異常系 |
| 4 | `unit` | `SlackClient` | `retry / timeout / 失敗時方針` | timeout 発生 | `Notify` | 仕様どおり retry または失敗する | 通信方針 |
| 5 | `integration` | `SlackClient` | `integration 契約確認` | テスト用 endpoint | `Notify` | 実 request 形式が契約と一致する | sandbox / mock server |
| 6 | `integration` | `SlackClient` | `回帰` | 過去に壊れた特殊文字入力 | `Notify` | payload 崩れが再発しない | 再発防止 |

補足:

- この例では repository 系観点を省略している。client adapter に不要な観点は無理に入れない
