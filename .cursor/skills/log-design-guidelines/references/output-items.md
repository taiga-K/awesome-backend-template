# 出力項目

## ログレベル

| レベル | 説明 | 目的 | ローカル | 開発 | 検証 | 本番 |
|--------|------|------|----------|------|------|------|
| FATAL | 致命的 | サービス停止。必須の環境変数が未設定など | ✅ | ✅ | ✅ | ✅ |
| ERROR | エラー | リクエスト処理失敗。予期せぬ例外など | ✅ | ✅ | ✅ | ✅ |
| WARN | 警告 | 将来対応が必要な状態。証明書期限切れ間近など | ✅ | ✅ | ✅ | ✅ |
| INFO | 情報 | システム正常性判断用。バッチ開始/終了など | ✅ | ✅ | ✅ | ✅ |
| DEBUG | デバッグ | 開発者向け詳細情報。SQLクエリなど | ✅ | ✅ | | |
| TRACE | トレース | DEBUGより更に詳細。メソッド開始/終了など | ✅ | | | |

### 推奨事項

- アプリからは **DEBUG〜ERROR** を利用する
- **TRACE、FATAL** はアプリからは利用しない（フレームワーク/共通ライブラリは利用可）
- デプロイメント環境推奨レベル:
  - 開発環境: DEBUG
  - ステージング/本番: INFO（大量ログの場合は事前にINFOへ切り上げ）
- 環境変数 `LOG_LEVEL` で切り替え可能にする

```go
// Go (slog) でのログレベル切り替え例
func logLevel() slog.Level {
    switch os.Getenv("LOG_LEVEL") {
    case "DEBUG":
        return slog.LevelDebug
    case "WARN":
        return slog.LevelWarn
    case "ERROR":
        return slog.LevelError
    default:
        return slog.LevelInfo
    }
}
```

- `/loggers` エンドポイントやJMXによる動的変更は非推奨

## 通知フラグ

大量の不要なアラート通知を避けるために、「本当に人間が確認すべきこと」を通知する設計が必要。

### 推奨事項

- 基本的にログレベル（WARN、ERROR）で通知制御を完結させる
- 通知フラグを導入する場合:
  - INFOレベルでも通知したいケース（重要なバッチ完了通知など）
  - メッセージ定義書だけで通知ON/OFFを切り替える必要がある場合

## メッセージコード

- 運用手順書と紐づけるため、開発者が一意に識別できるコードを付与する
- **WARN以上のレベルには設定必須**
- INFOレベルは不要（通知対象外のため）

```go
slog.Warn("在庫更新がデータ競合により失敗しました。（楽観ロック）",
    slog.String("message.code", "BIZ-W-1001"),
    slog.String("order.id", orderID),
)

slog.Error("決済処理に失敗しました。",
    slog.String("error.code", "PAYMENT-003"),
    slog.String("exception.type", "PaymentAPIError"),
    slog.String("exception.message", err.Error()),
)
```

## トレースID

上流で払い出して出力する。

- クライアント側統制可能: クライアント側で生成
- 統制不可: サーバーのミドルウェア層で発番

```go
// ミドルウェアでトレースIDをcontextに設定するパターン
func TraceMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        traceID := r.Header.Get("X-Trace-ID")
        if traceID == "" {
            traceID = uuid.NewString()
        }
        ctx := context.WithValue(r.Context(), traceIDKey, traceID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

## ユーザーメッセージとログの分離

### 推奨事項

- ログメッセージと、ユーザー向けエラーメッセージは分離管理する
- セキュリティリスク回避（詳細情報は攻撃のヒントになる）
- 保守性向上
- トレースIDをユーザーメッセージにも出力し、紐づけ可能にする

### 開発者向けログ例

```json
{
  "timestamp": "2025-09-12T14:46:16.234+09:00",
  "severity": "ERROR",
  "message": "決済処理に失敗しました。",
  "service.name": "payment-service",
  "logger.name": "payment",
  "error.id": "E-1a2b3c4d",
  "error.code": "PAYMENT-003",
  "exception.type": "PaymentAPIError",
  "exception.message": "Credit card company timeout"
}
```

### ユーザー向けメッセージ例

```
決済処理中にエラーが発生しました。お手数ですが、時間をおいて再度お試しください。
解決しない場合は、サポートまでお問い合わせください。
(エラーコード: E10222  トレースID: E-00112233)
```

## メッセージの書き方

### 推奨事項

- 具体的かつ一意に解釈できるように記述する
  - NG: `"DB error occurred."`
  - OK: `"Failed to INSERT into products table. Cause: primary key duplicate. productId: 12345"`
- 調査で切り分けに使える識別子を含める
- Goでは `context` で自動付与する
- 事実とデータを分離する
  - テンプレート（事実）と可変値（データ）を分離する
  - 可変値は構造化ログとして個別キーで切り出す

### 良い例: 可変値をフラットに出力

```go
slog.Info("Cart item stock allocation failed.",
    slog.String("user.id", "user-456"),
    slog.String("sku.cd", "ABC-123-XYZ-RED-L"),
)
```

出力:
```json
{
  "timestamp": "2025-08-26T10:36:17.123+09:00",
  "severity": "INFO",
  "message": "Cart item stock allocation failed.",
  "user.id": "user-456",
  "sku.cd": "ABC-123-XYZ-RED-L"
}
```

### 悪い例1: メッセージ本文に埋め込み

```go
// NG: 検索・フィルタリングが困難
slog.Info(fmt.Sprintf("Cart item stock allocation failed. (userID: %s SKU: %s)", userID, sku))
```

### 悪い例2: details配下にネスト

```go
// NG: フラットでないためクエリが複雑になる
slog.Info("Cart item stock allocation failed.",
    slog.Group("details",
        slog.String("user.id", "user-456"),
        slog.String("sku.cd", "ABC-123-XYZ-RED-L"),
    ),
)
```
