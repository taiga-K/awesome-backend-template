# スキーマとキー名

## 共通スキーマ

全ログでまず揃える項目は以下。

| 役割 | 推奨キー | Go `slog` での実装上の扱い |
| --- | --- | --- |
| タイムスタンプ | `timestamp` | 既定の `time` でも可。共通ハンドラで寄せてもよい |
| 重大度 | `severity.text` | 既定の `level` でも可 |
| メッセージ | `message` | 既定の `msg` でも可 |
| サービス名 | `service.name` | 共通属性で付与する |
| バージョン | `service.version` | 起動時または共通属性で付与する |
| 環境 | `deployment.environment` | 共通属性で付与する |
| トレース ID | `trace_id` | ミドルウェアで付与する |
| スパン ID | `span_id` | トレーシング導入時に付与する |

補足:

- コード上は `slog` 既定の `time` / `level` / `msg` を使ってもよい
- 収集基盤や共通ハンドラで `timestamp` / `severity.text` / `message` へ正規化する責務を明確にする

## 基本ルール

- キー名は `dot.case` を基本にする
- 追加属性はフラットに持たせる
- `details` のような入れ子に可変値をまとめない
- 分析基盤やクエリが使いやすい粒度で切る

## HTTP でよく使う項目

- `request.id`
- `http.request.method`
- `http.response.status_code`
- `url.path`
- `client.address`
- `user_agent.original`
- `http.request.body.size`
- `http.server.request.duration`

補足:

- `client.address` は個人情報の扱いに注意する
- `request.id` と `trace_id` はどちらか片方に寄せてもよいが、役割は明確にする
- アクセスログはヘルスチェックを除外する

## DB でよく使う項目

- `db.system`
- `db.operation`
- `db.statement`
- `db.duration`

補足:

- `db.statement` は機密値や巨大な SQL を含めないように注意する
- バインド値の生出力が危険なら、テンプレート SQL や操作種別だけに落とす

## 例外でよく使う項目

- `exception.type`
- `exception.message`
- `exception.stack_trace`
- `event.kind`
- `event.category`
- `event.outcome`

補足:

- スタックトレースは開発者向けログであり、ユーザー向けメッセージへ流さない
- 同一例外の重複ログは避ける

## 業務イベントでよく使う項目

- `message.code`
- `user.id`
- `tenant.id`
- `order.id`
- `product.id`
- `batch.job_id`

補足:

- 業務 ID は文字列連結ではなく個別キーに分ける
- 運用者が追う必要のあるイベントだけメッセージコードを持たせる

## `slog` での書き方

良い例:

```go
logger.InfoContext(ctx, "inventory allocation failed",
    "user.id", userID,
    "product.sku", skuCode,
    "trace_id", traceID,
)
```

避ける例:

```go
logger.InfoContext(ctx, "inventory allocation failed: user="+userID+" sku="+skuCD)
```
