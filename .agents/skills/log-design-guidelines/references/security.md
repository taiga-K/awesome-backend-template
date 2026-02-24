# セキュリティ

## 機密情報の取り扱い

### ログに出力してはいけない情報

- セッションID
- アクセストークン / リフレッシュトークン
- パスワード
- APIキー
- クレジットカード番号
- 個人情報（PII）
- GDPR未同意情報

### マスキング

機密情報をログ出力する必要がある場合は、必ずマスキングする。

```go
// マスキングユーティリティの例
func maskEmail(email string) string {
    parts := strings.SplitN(email, "@", 2)
    if len(parts) != 2 {
        return "***"
    }
    local := parts[0]
    if len(local) <= 2 {
        return "***@" + parts[1]
    }
    return local[:2] + "***@" + parts[1]
}

func maskCardNumber(card string) string {
    if len(card) < 4 {
        return "****"
    }
    return strings.Repeat("*", len(card)-4) + card[len(card)-4:]
}
```

### フレームワーク側でのマスキング

- DTOやレスポンス構造体で機密フィールドを除外する
- `String()` / `GoString()` メソッドで機密フィールドをマスクする

```go
type User struct {
    ID       string `json:"id"`
    Email    string `json:"email"`
    Password string `json:"-"` // JSONシリアライズから除外
}

// String() でログ出力時に機密情報をマスク
func (u User) String() string {
    return fmt.Sprintf("User{ID: %s, Email: %s}", u.ID, maskEmail(u.Email))
}

// LogValue() で slog での出力をカスタマイズ
func (u User) LogValue() slog.Value {
    return slog.GroupValue(
        slog.String("id", u.ID),
        slog.String("email", maskEmail(u.Email)),
    )
}
```

## アクセス制御

- **ログ改ざん防止**: IAMロール設定で変更・削除不可にする
  - Google Cloud Logging では `roles/logging.viewer`（読み取り専用）を基本とする
  - `roles/logging.admin` は最小限のメンバーに限定する
- **閲覧制限**: 必要メンバーのみがログにアクセスできるようにする

## ユーザー向けログと開発者向けログの分離

### 理由

- スタックトレース、DBエラーメッセージ等は攻撃のヒントになる
- ユーザー向けはユーザーフレンドリーな表示にする
- 詳細は開発者向けログに記録する

### 実装パターン

```go
// エラーレスポンスでは詳細を隠す
type ErrorResponse struct {
    Code    string `json:"code"`
    Message string `json:"message"`    // ユーザー向けメッセージ
    TraceID string `json:"trace_id"`   // ログとの紐づけ用
}

func handleError(w http.ResponseWriter, r *http.Request, err error, traceID string) {
    // 開発者向けログ: 詳細情報を全て出力
    slog.Error("リクエスト処理に失敗しました。",
        slog.String("trace_id", traceID),
        slog.String("error.code", "PAYMENT-003"),
        slog.String("exception.type", fmt.Sprintf("%T", err)),
        slog.String("exception.message", err.Error()),
        slog.String("url.path", r.URL.Path),
    )

    // ユーザー向けレスポンス: 最小限の情報のみ
    resp := ErrorResponse{
        Code:    "E10222",
        Message: "決済処理中にエラーが発生しました。お手数ですが、時間をおいて再度お試しください。",
        TraceID: traceID,
    }
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(http.StatusInternalServerError)
    json.NewEncoder(w).Encode(resp)
}
```
