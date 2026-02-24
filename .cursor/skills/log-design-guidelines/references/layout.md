# レイアウト

## ログフォーマット: JSON Lines

ログフォーマットは **JSON Lines** を採用する。

### 採用理由

- RFC 8259で標準化されている
- 複数のデータ型に対応
- Google Cloud Logging、BigQuery等で広くサポートされている
- 構造化ログとして検索・フィルタリングが容易

### 非採用フォーマットとその理由

| フォーマット | 非採用理由 |
|-------------|-----------|
| Apache Combined Format | 信頼できる仕様が存在しない |
| LTSV | 信頼できる仕様が存在しない |
| OTLP/JSON | 深くネストされた複雑な構造で分析性が低下 |

## Go (slog) での JSON Lines 出力

```go
// slog.NewJSONHandler で JSON Lines 形式のログを標準出力に出力する
handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
    ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
        if a.Key == slog.LevelKey {
            a.Key = "severity"
        }
        if a.Key == slog.TimeKey {
            a.Key = "timestamp"
        }
        if a.Key == slog.MessageKey {
            a.Key = "message"
        }
        return a
    },
})
slog.SetDefault(slog.New(handler))
```

## ローカル環境での表示

ローカル環境では JSON Lines ではなく非構造なログ形式も許容する。

### テキストハンドラの利用

```go
// ローカル環境では slog.NewTextHandler で可読性の高いログを出力
func newLogger(env string) *slog.Logger {
    var handler slog.Handler
    if env == "local" {
        handler = slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelDebug,
        })
    } else {
        handler = slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
            Level: slog.LevelInfo,
            ReplaceAttr: replaceAttr,
        })
    }
    return slog.New(handler)
}
```

### ローカル環境限定の絵文字表示例

```
DEBUG: Order #ORD-123 の処理を開始します。現在のステータス: PENDING ⏳
DEBUG: 在庫を確認中... 商品ID: P-123 の在庫は 10個です ✅
DEBUG: 注文ステータスを PROCESSING ⚙️ に更新しました。
DEBUG: 最終的な合計金額を計算しました: 💰 10000円
DEBUG: ユーザー customer@example.com 宛に確認メールを送信します 📧
DEBUG: 注文ステータスを COMPLETED ✨ に更新しました。
DEBUG: Order #ORD-123 の処理が正常に完了しました 🎉
```

- デプロイメント環境では絵文字を出さない

### ANSIエスケープシーケンス

原則利用しない。クラウド環境ではパース負荷がかかり、エスケープミスの事故が多いため。
