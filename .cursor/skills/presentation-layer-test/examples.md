# 例

## 例1: handler `PostProducts`

前提:

- `PostProducts` は JSON request を bind して `CreateUseCase` を呼ぶ
- 成功時は 201 と response body を返す
- bind error や usecase error は presentation で client 向けに変換する

項目表:

| No | テスト種別 | 対象 | 観点 | 事前状態/入力 | 実行 | 期待結果 | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | `unit` | `PostProducts` | `request mapping` | 正常な request struct | handler 内変換 | `CreateInput` へ正しく詰め替える | 基本ケース |
| 2 | `unit` | `PostProducts` | `usecase 呼び出し` | 正常入力 | handler 実行 | 正しい usecase を呼ぶ | 余計な調停をしない |
| 3 | `unit` | `PostProducts` | `response mapping` | usecase 成功 output | handler 実行 | `ProductResponse` へ変換する | 基本ケース |
| 4 | `unit` | `PostProducts` | `表示用書式変換` | price を含む output | handler 実行 | 表示用 price に整形する | presentation の責務 |
| 5 | `unit` | `PostProducts` | `error mapping` | usecase error | handler 実行 | client 向け error response へ変換する | status 以外の整形 |
| 6 | `handler integration` | `PostProducts` | `request parsing` | 正常な JSON body | `POST /products` | bind 成功して 201 を返す | `httptest` |
| 7 | `handler integration` | `PostProducts` | `request validation` | 必須項目欠落 | `POST /products` | 400 を返す | API 制約 |
| 8 | `handler integration` | `PostProducts` | `HTTP status / response code` | 作成成功 | `POST /products` | 201 を返す | 成功 status |
| 9 | `handler integration` | `PostProducts` | `HTTP status / response code` | bind 失敗 | `POST /products` | 400 を返す | bind error |
| 10 | `handler integration` | `PostProducts` | `回帰` | 過去に壊れた特殊入力 | `POST /products` | response format 崩れが再発しない | 再発防止 |

補足:

- この例では `認証 / セッション bridge` と `middleware / routing` を省略している。認証必須 endpoint なら追加する
- `request parsing` と `HTTP status / response code` は同じシナリオで一緒に確認できる。重なりが強い場合は 1 行へ統合してよい

## 例2: 認証 middleware / session bridge

前提:

- middleware は framework の認証結果を抽象的な session 情報へ変換する
- 認証失敗時は usecase を呼ばずに早期終了する

項目表:

| No | テスト種別 | 対象 | 観点 | 事前状態/入力 | 実行 | 期待結果 | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | `unit` | `AuthMiddleware` | `認証 / セッション bridge` | 認証済み情報 | middleware 実行 | 必要な session 抽象へ変換する | framework 情報を閉じる |
| 2 | `unit` | `AuthMiddleware` | `framework 依存の隔離` | framework auth 型 | middleware 実行 | usecase へ framework 型を渡さない | 境界確認 |
| 3 | `handler integration` | `AuthMiddleware` | `middleware / routing` | 認証必須 route | HTTP request | middleware が endpoint に適用される | router 確認 |
| 4 | `handler integration` | `AuthMiddleware` | `HTTP status / response code` | 未認証 | HTTP request | 401 または 403 を返す | 仕様次第 |
| 5 | `handler integration` | `AuthMiddleware` | `回帰` | 過去に bypass できた条件 | HTTP request | 再発しない | 認証漏れ防止 |

補足:

- この例では request / response mapping を省略している。middleware 単体では不要な観点は無理に入れない
