# 出力ルール

## フロントエンドのログ出力

フロントエンドでは基本的にログ出力を行わない。

### 理由

- デバッグ情報が一般ユーザーに見える情報漏洩リスク
- コード読みやすさの低下
- ESLint、Biomeで警告される

クライアントエラー収集が必要な場合は Sentry などログ基盤導入を検討する。

## 起動時のログ出力

### ログレベル: INFO

### 出力項目

| 項目 | 概要 | 例 |
|------|------|-----|
| サービス名 | どのサービスか明確化 | user-api |
| バージョン情報 | git tag情報など | v1.2.3 |
| Gitハッシュ | ビルド時の値 | da94541 |
| タイムスタンプ | ビルド時（起動時ではなく）JSTまたはUTC | 2025-09-12T14:46:16.234+09:00 |
| 実行環境 | 環境区別 | production |
| 主要な設定値 | DB接続先など（機密情報は除外） | DB_HOST: prod-db.example.com |

### マイルストーン出力

起動完了までの主要ステップをログ出力し、失敗時の特定を容易にする。

### Go での起動ログ実装例

```go
// ビルド時にldflags で埋め込む変数
var (
    version   string
    gitHash   string
    buildTime string
)

func logStartupBanner(env string) {
    banner := fmt.Sprintf(`
  ==================================================
  Service: UserAPI
  Ver: %s
  GitHash: %s
  Timestamp: %s
  ENV: %s
  ==================================================`, version, gitHash, buildTime, env)
    fmt.Println(banner)

    slog.Info("アプリケーション起動シーケンスを開始します。")
    slog.Info("設定の読み込みが完了しました。")
    slog.Info("データベース接続が確立しました。")
    slog.Info("サーバーがリッスンを開始しました。",
        slog.String("addr", "0.0.0.0:8080"),
    )
}
```

## Web APIのログ出力

### アクセスログの出力タイミング

推奨順:
1. **リクエスト/レスポンス両方で出力**（最推奨。ログ量は倍だが保守運用性向上）
2. レスポンス後に出力（処理時間やステータスコード出力可）
3. リクエスト到達時に出力

### 除外すべきログ

- ヘルスチェックのアクセスログ（システム内部利用のため）

### OPTIONSメソッド

APIゲートウェイで対応が推奨だが、アプリ側で実装する場合はログを出す（トラブルシューティング・セキュリティ監視に有用）。

### ログ項目

| 項目 | 要求時 | 応答時 | 備考 |
|------|--------|--------|------|
| timestamp | ✅ | ✅ | ISO 8601形式でミリ秒。UTC または JST |
| severity | ✅ | ✅ | info固定または要求時debug・応答時info |
| request.id | ✅ | ✅ | トレース用ID。ヘッダーに存在すればそれ、なければサーバー採番 |
| url.path | ✅ | ✅ | 相対パス例: /api/v1/users |
| http.request.method | ✅ | ✅ | HEAD, GET, POST, PUT, PATCH, DELETE |
| client.address | ❓ | ❓ | セキュリティ基準に従う |
| user_id | ❓ | ❓ | ログイン済みの場合 |
| http.response.status_code | | ✅ | HTTPステータスコード |
| http.server.request.duration | | ✅ | ミリ秒推奨 |
| user_agent.original | ✅ | ✅ | クライアント特定に利用 |

### Go でのアクセスログミドルウェア例

```go
func AccessLogMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // ヘルスチェックは除外
        if r.URL.Path == "/health" {
            next.ServeHTTP(w, r)
            return
        }

        start := time.Now()
        traceID := r.Header.Get("X-Trace-ID")
        if traceID == "" {
            traceID = uuid.NewString()
        }

        // リクエストログ
        slog.Info("リクエストを受信しました。",
            slog.String("trace_id", traceID),
            slog.String("http.request.method", r.Method),
            slog.String("url.path", r.URL.Path),
            slog.String("user_agent.original", r.UserAgent()),
        )

        // レスポンスをラップしてステータスコードを取得
        rw := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}
        next.ServeHTTP(rw, r)

        // レスポンスログ
        duration := time.Since(start)
        slog.Info("レスポンスを送信しました。",
            slog.String("trace_id", traceID),
            slog.String("http.request.method", r.Method),
            slog.String("url.path", r.URL.Path),
            slog.Int("http.response.status_code", rw.statusCode),
            slog.Int64("http.server.request.duration_ms", duration.Milliseconds()),
        )
    })
}
```

## バッチ実行時のログ出力

### 推奨事項

- 起動・終了はログ出力する（機能ID、バージョン、実行時間、パラメータ）
- 処理件数をログ出力する（0件の場合もその旨を出す）
- 進行中のログを出す（1万件ごとなど）
  - ハングか進行中かの判別に有用
- SQL実行ログは生成後SQLをフォーマットして出す
- ループ処理ログはセーブする（Google Cloud Loggingのコストが高いため）

### バッチログ出力例

```go
// 開始時
slog.Info("Monthly aggregation batch started.",
    slog.String("batch.job_id", "monthly-aggregate"),
    slog.String("batch.params.target_month", "2025-09"),
)

// 進行中（サンプリング）
slog.Info("Aggregation processing in progress.",
    slog.Int("batch.progress.completed", 10000),
    slog.Int("batch.progress.total", 50000),
    slog.String("batch.progress.percentage", "20%"),
)

// 終了時
slog.Info("Monthly aggregation batch completed successfully.",
    slog.String("batch.result", "success"),
    slog.Int("batch.stats.total", 50000),
    slog.Int("batch.stats.success", 49998),
    slog.Int("batch.stats.failed", 2),
    slog.Int("batch.stats.skipped", 0),
    slog.Int64("duration_ms", 120500),
)
```

## 非正規化

分析に必要なユーザー属性をログ項目として出力する。会員ランクなどの属性をマスタから引き当てせず、ログ出力時に振り下ろすことで分析コストを削減する。

## 暗黙的なログ項目・明示的なログ項目

ライフサイクルを明記した一覧表を作成すること。

| 出力場所 | トリガー | 項目種別 | 項目例 | 補足説明 |
|----------|----------|----------|--------|-----------|
| フレームワーク | リクエスト単位 | HTTPリクエスト | ステータス、パス、処理時間、リクエスト元IP | Webフレームワークが自動記録 |
| | | DBアクセス | SQLクエリなど | |
| | 例外発生時 | 例外 | メッセージ、レベル | フレームワークでレベル決定 |
| アプリケーション | アプリ呼び出し | ロガー出力項目 | ファイル名、行番号など | slogが自動取得 |
| | | コンテキスト設定項目 | ユーザーID、トレースID、トランザクションID | context.Contextで後続処理に引き継ぎ |
| | | 暗黙的設定項目 | パッケージ名（ロガー名） | ロガー初期化時に指定 |
| | | 明示的出力項目 | エラーメッセージ、ステータス、パラメータ | 開発者が実装 |
| | ログレベル指定 | ログレベル | slog.Error()のように指定 | |
