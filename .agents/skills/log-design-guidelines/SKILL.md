---
name: log-design-guidelines
description: "アプリケーションログ設計のガイドライン。Google Cloudまたはローカル環境での標準出力ベースのログを対象とし、Go言語（log/slog）での実装を前提とする。ログメッセージは日本語で記述し、キー名はOTel準拠の英語dot.caseを使用する。出典: Future Architect ログ設計ガイドライン (https://future-architect.github.io/arch-guidelines/documents/forLog/log_guidelines.html)。使用タイミング: (1) ログ出力処理を新規実装するとき、(2) 既存のログ出力をレビュー・改善するとき、(3) ログのキー名や出力項目を設計するとき、(4) Web APIやバッチのアクセスログを設計するとき、(5) ログレベルの使い分けを判断するとき、(6) ログのセキュリティ・マスキングを検討するとき、(7) ログコスト最適化を検討するとき、(8) 運用手順書と紐づくメッセージコードを設計するとき。キー命名規則、レイアウト、出力項目、出力ルール、メッセージ言語方針、セキュリティ、性能、費用を網羅。"
---

# ログ設計ガイドライン

Google Cloud またはローカル環境での標準出力ベースのアプリケーションログ設計指針。
Go言語（log/slog）での実装を前提とする。ログメッセージは日本語、キー名はOTel準拠の英語。

出典: [Future Architect ログ設計ガイドライン](https://future-architect.github.io/arch-guidelines/documents/forLog/log_guidelines.html)

## 対象スコープ

- アプリケーションログが対象（バックエンド領域）
- Cloud Audit Logs、VPC フローログなど Google Cloud サービス側のログは対象外
- Google Cloud またはローカル環境での実行を前提
- 標準出力ベースのログ
- ログメッセージは日本語で記述する（多言語対応の予定なし）

## リファレンスファイル

詳細なガイドラインはトピック別に分割。作業に関連するファイルを参照すること。

- **[references/key-naming.md](references/key-naming.md)** — ログキー命名規則、OTel/ECS比較、共通スキーマ、拡張スキーマ、Google Cloud Logging対応
- **[references/layout.md](references/layout.md)** — ログフォーマット（JSON Lines）、ローカル環境での表示、非構造ログ
- **[references/output-items.md](references/output-items.md)** — ログレベル、通知フラグ、メッセージコード、トレースID、メッセージの書き方、可変値の分離
- **[references/output-rules.md](references/output-rules.md)** — 起動時ログ、Web APIアクセスログ、バッチ実行ログ、非正規化、暗黙的/明示的ログ項目
- **[references/message-language.md](references/message-language.md)** — 日本語ログメッセージの書き方、キー名は英語dot.case、ユーザー向けメッセージ
- **[references/security.md](references/security.md)** — 機密情報のマスキング、アクセス制御、ユーザー向け/開発者向けログの分離
- **[references/performance.md](references/performance.md)** — Go（slog）での性能考慮事項、マシンガンログの回避、ファイル名・行番号の負荷
- **[references/cost.md](references/cost.md)** — Google Cloud Logging費用最適化、保持期間ポリシー、ログ量の制御
- **[references/documentation.md](references/documentation.md)** — メッセージ定義書、運用手順書との紐づけ、ログ項目ライフサイクル

## クイックリファレンス: 基本方針

1. **OTel準拠** — ログキーはOpenTelemetry規約に準拠し、ベンダーロックインを回避
2. **JSON Lines** — ログフォーマットはJSON Lines（RFC 8259）を採用
3. **構造化ログ** — 可変値はメッセージ本文に埋め込まず、個別キーとしてフラットに出力
4. **日本語メッセージ** — ログメッセージは日本語で記述。キー名はOTel準拠の英語dot.case
5. **機密情報の排除** — パスワード、トークン、PII等はログに出力しない。必要な場合はマスキング

## クイックリファレンス: Go (slog) でのログ出力

```go
// slog を使った構造化ログの基本パターン
slog.Info("決済処理が完了しました。",
    slog.String("order.id", orderID),
    slog.String("user.id", userID),
    slog.Int64("amount", amount),
)

// エラーログ
slog.Error("決済処理に失敗しました。",
    slog.String("error.code", "PAYMENT-003"),
    slog.String("exception.type", "PaymentAPIError"),
    slog.String("exception.message", err.Error()),
    slog.String("order.id", orderID),
)

// contextからトレースIDを自動付与するパターン
logger := slog.With(
    slog.String("trace_id", traceIDFromCtx(ctx)),
    slog.String("span_id", spanIDFromCtx(ctx)),
    slog.String("service.name", "payment-service"),
)
logger.Info("リクエストを受信しました。",
    slog.String("http.request.method", r.Method),
    slog.String("url.path", r.URL.Path),
)

// ログレベル: DEBUG〜ERRORを使用（TRACE/FATALはアプリからは使わない）
// 可変値はメッセージに埋め込まず、個別キーとしてフラットに出力する
// メッセージは日本語で、「何が」「どうなったか」を具体的に記述する
// キー名はOTel準拠の英語dot.caseを使用する
```

## クイックリファレンス: Google Cloud Logging 対応

```go
// Google Cloud Logging は severity フィールドでログレベルを認識する
// slog の JSON ハンドラでキーをリマップする例
handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
    ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
        // Google Cloud Logging 用に level → severity へリマップ
        if a.Key == slog.LevelKey {
            a.Key = "severity"
        }
        // timestamp キーに統一
        if a.Key == slog.TimeKey {
            a.Key = "timestamp"
        }
        // msg → message に統一
        if a.Key == slog.MessageKey {
            a.Key = "message"
        }
        return a
    },
})
slog.SetDefault(slog.New(handler))
```
