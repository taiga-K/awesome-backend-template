# ログキー命名規則

## 標準的な規約

主要な規約として **OpenTelemetry (OTel)** と **Elastic Common Schema (ECS)** がある。2023年にOTelにECSが統合された。

### OTel vs ECS 比較

| 項目 | OpenTelemetry | ECS |
|------|---------------|-----|
| 焦点 | オブザーバビリティ（トレース、メトリクス、ログの相関） | セキュリティ分析とSIEM |
| 構造 | フラットなAttributes | ネストされたJSON |
| 命名規則 | dot.case | dot.case |
| タイムスタンプ | timestamp | @timestamp |
| メッセージ | body | message |

### 方針

- **OTel準拠**とECSの語彙を取り入れる
- **プラットフォーム非依存**を原則とする
- ベンダーロックインを避けるため、OTelの規則を使用し、OTelエクスポーターで各プラットフォーム仕様にマッピングする
- 共通スキーマと拡張スキーマの階層構造を採用する

## Go (slog) のデフォルトキー名

| 項目 | slog デフォルト |
|------|----------------|
| タイムスタンプ | time |
| メッセージ | msg |
| ログレベル | level |
| ソース情報 | source |

Google Cloud Logging で認識させるため、`ReplaceAttr` で以下のようにリマップする:
- `time` → `timestamp`
- `msg` → `message`
- `level` → `severity`

## Google Cloud Logging のキー名

| 項目 | Google Cloud Logging |
|------|----------------------|
| タイムスタンプ | timestamp |
| ログメッセージ | jsonPayload |
| ログレベル | severity |
| トレース連携 | trace、spanId |
| HTTPリクエスト | httpRequest |
| カスタム属性 | labels |

## 共通スキーマ（コアフィールド）

全てのログに含めるべき基本項目。

| キー名 | 説明 | 例 | 理由 |
|--------|------|-----|------|
| timestamp | ISO 8601形式のタイムスタンプ | "2025-08-26T10:30:00.123456789Z" | OTel, ECS両方で必須 |
| severity | 重大度レベル（Google Cloud Logging対応） | "ERROR" | OTel: severity.text に相当。Google Cloud Logging は severity で認識 |
| message | ログの主要なペイロード | "User login failed" | OTel Bodyに相当 |
| service.name | サービス識別 | "authentication-service" | OTel, ECS, DataDog, New Relicで中核 |
| service.version | バージョン | "1.2.3" | リリース追跡に必須 |
| deployment.environment | 環境 | "production" | 環境フィルタリングに必須 |
| trace_id | 分散トレースへのリンク | "a1b2c3d4e5f6..." | OTel, ECS, New Relicに準拠 |
| span_id | トレース内の操作へのリンク | "f1e2d3c4b5a6..." | OTel, ECS, New Relicに準拠 |

## 拡張スキーマ

### HTTP要求/応答

| キー名 | 説明 | 例 |
|--------|------|-----|
| http.request.method | HTTPメソッド | "GET" |
| http.response.status_code | ステータスコード | 200 |
| url.path | リクエストURL | "/users/123?query=abc" |
| user_agent.original | ユーザーエージェント | "Mozilla/5.0..." |
| client.address | クライアントIP | "192.0.2.1" |
| http.request.body.size | リクエストボディサイズ | 1024 |
| http.server.request.duration | 処理時間（ナノ秒） | 125000000 |

### DB

| キー名 | 説明 | 例 |
|--------|------|-----|
| db.system | データベースの種類 | "postgresql" |
| db.statement | SQL文 | "SELECT * FROM users WHERE id = ?" |
| db.operation | 実行操作 | "SELECT" |
| db.duration | クエリ実行時間（ナノ秒） | 15000000 |

### 例外

| キー名 | 説明 | 例 |
|--------|------|-----|
| exception.type | 例外/エラーの型名 | "PaymentAPIError" |
| exception.message | エラーメッセージ | "Credit card company timeout" |
| exception.stack_trace | スタックトレース | "goroutine 1 [running]:..." |
| event.kind | イベントの種類 | "event" |
| event.category | イベントのカテゴリ | "error" |
| event.outcome | イベントの結果 | "failure" |

## OTelログデータ例

```json
{
  "logRecords": [
    {
      "timeUnixNano": "1724737589123456789",
      "severityText": "ERROR",
      "body": {
        "stringValue": "Payment processing failed due to insufficient funds"
      },
      "attributes": [
        {"key": "http.request.method", "value": {"stringValue": "POST"}},
        {"key": "http.route", "value": {"stringValue": "/api/v1/payment"}},
        {"key": "customer.id", "value": {"stringValue": "customer-00123"}}
      ],
      "traceId": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
      "spanId": "1a2b3c4d5e6f7a8b"
    }
  ]
}
```

## SaaSオブザーバビリティプラットフォームとの対応

| 項目 | DataDog | New Relic | OpenTelemetry |
|------|---------|-----------|---------------|
| トレースID | dd.trace_id | trace.id | trace_id |
| スパンID | dd.span_id | span.id | span_id |
| サービス名 | service | entity.name | service.name |
| 環境 | env | （カスタム属性） | deployment.environment |
| バージョン | version | （カスタム属性） | service.version |
| ホスト | host | hostname | host.name |
