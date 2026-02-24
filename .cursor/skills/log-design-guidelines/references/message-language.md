# メッセージ言語方針

## 基本方針

- ログメッセージは **日本語** で記述する
- 多言語対応の予定はない
- メッセージコードを付与し、運用手順書と紐づける

## 日本語ログメッセージの書き方

### 原則

- 具体的かつ一意に解釈できる日本語で記述する
- 体言止めや曖昧な表現を避け、「何が」「どうなったか」を明確にする
- 可変値はメッセージ本文に埋め込まず、構造化ログのキーとして分離する

### 良い例

```go
slog.Info("月次集計バッチを開始します。",
    slog.String("batch.job_id", "monthly-aggregate"),
    slog.String("batch.params.target_month", "2025-09"),
)

slog.Error("商品テーブルへのINSERTに失敗しました。原因: 主キー重複。",
    slog.String("error.code", "PRODUCT-E-001"),
    slog.String("product.id", "12345"),
    slog.String("exception.message", err.Error()),
)

slog.Warn("カート追加時の在庫引当に失敗しました。",
    slog.String("message.code", "BIZ-W-1001"),
    slog.String("user.id", "user-456"),
    slog.String("sku.cd", "ABC-123-XYZ-RED-L"),
)
```

### 悪い例

```go
// NG: 曖昧な表現
slog.Error("DBエラーです。")

// NG: 可変値をメッセージに埋め込んでいる
slog.Info(fmt.Sprintf("ユーザー %s のカート追加時に在庫引当失敗（SKU: %s）", userID, sku))
```

## ログキー名は英語（dot.case）

メッセージは日本語だが、**ログキー名はOTel準拠の英語dot.case**を使用する。

```json
{
  "timestamp": "2025-08-26T10:36:17.123+09:00",
  "severity": "WARN",
  "message": "カート追加時の在庫引当に失敗しました。",
  "message.code": "BIZ-W-1001",
  "user.id": "user-456",
  "sku.cd": "ABC-123-XYZ-RED-L",
  "service.name": "cart-service",
  "trace_id": "a1b2c3d4e5f6a7b8"
}
```

## ユーザー向けメッセージ

ユーザー向けエラーメッセージも日本語で記述する。トレースIDを含めてログとの紐づけを可能にする。

```
決済処理中にエラーが発生しました。お手数ですが、時間をおいて再度お試しください。
解決しない場合は、サポートまでお問い合わせください。
(エラーコード: E10222  トレースID: E-00112233)
```
