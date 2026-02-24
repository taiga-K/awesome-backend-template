# 性能

## Go (slog) での性能考慮事項

Go の標準ライブラリ `log/slog` は十分な性能を持つため、非同期ロギングは不要。

### 遅延評価の活用

slog では属性を `slog.Attr` として渡すことで、不要なレベルのログでは文字列変換が発生しない。

```go
// 良い例: slog のAttr を使用（遅延評価される）
slog.Debug("ユーザーデータを処理しています。",
    slog.String("user.id", userID),
    slog.Any("payload", payload),
)

// 悪い例: fmt.Sprintf で事前に文字列変換（常に評価される）
slog.Debug(fmt.Sprintf("ユーザーデータを処理しています: %v", payload))
```

### ログ出力の分岐

特に文字列加工が重い場合は、ログレベルの確認で分岐する。

```go
// 重い処理を伴うログ出力は、レベルチェックで囲む
if slog.Default().Enabled(context.Background(), slog.LevelDebug) {
    details := expensiveDebugInfo()
    slog.Debug("処理の詳細情報。",
        slog.String("details", details),
    )
}
```

## マシンガンログの回避

forループ内で毎回ログを出力しない。サンプリングで出力する。

```go
// 悪い例: 全件ログ出力（マシンガンログ）
for i, item := range items {
    slog.Debug("アイテムを処理しています。",
        slog.Int("index", i),
        slog.String("item.id", item.ID),
    )
    process(item)
}

// 良い例: サンプリング（1000件に1度 + 最終件）
for i, item := range items {
    if i%1000 == 0 {
        slog.Info("アイテム処理を実行中です。",
            slog.Int("progress.completed", i),
            slog.Int("progress.total", len(items)),
        )
    }
    process(item)
}
slog.Info("全アイテムの処理が完了しました。",
    slog.Int("total", len(items)),
)
```

## ファイル名・行番号の取得コスト

- スタックトレース取得は負荷が高い
- slog の `AddSource` オプションはローカル環境のみ許容する
- デプロイメント環境ではソース情報を無効化する

```go
func newHandler(env string) slog.Handler {
    opts := &slog.HandlerOptions{
        Level:     logLevel(),
        AddSource: env == "local", // ローカルのみソース情報を付与
        ReplaceAttr: replaceAttr,
    }
    return slog.NewJSONHandler(os.Stdout, opts)
}
```

## 性能問題の切り分け

性能問題が発生した場合、ログ出力を疑う。特に以下のケースに注意:
- SQLログ等の大量出力
- 巨大なペイロードのログ出力
- ループ内での無制限なログ出力

## エラー時のバッファリング

Go の `os.Stdout` は行バッファリングされるため、通常はクラッシュ時のログ喪失リスクは低い。ただし、カスタムのバッファ付きWriterを使用している場合は、WARN以上のログで自動フラッシュを行うことを検討する。
