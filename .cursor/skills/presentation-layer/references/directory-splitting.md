# `internal/presentation` の肥大化判断と分割

## いつ使うか

- `internal/presentation` をどう切るか相談されたとき
- handler が増えて構成を整理したいとき
- middleware や shared response の置き場を決めたいとき

## 基本原則

- 最初の分割軸は **業務機能または endpoint 群** にする
- `handler.go`, `request.go`, `response.go` を近くに置き、入口を追いやすくする
- framework 設定や middleware は `settings` や `shared` に分けてよい
- `common`, `util`, `misc` を最初から増やさない

## 基本形

```text
internal/presentation/
├─ products/
│  ├─ handler.go
│  ├─ request.go
│  └─ response.go
├─ orders/
│  ├─ handler.go
│  ├─ request.go
│  └─ response.go
└─ settings/
   ├─ middleware.go
   └─ error_handler.go
```

## こう分ける理由

- request と response がその handler の近くにあると追いやすい
- usecase ごとの入口が分かりやすい
- presentation 特有の framework 依存をその場で閉じ込めやすい

## 肥大化シグナル

- 1 handler ファイルに複数 endpoint 群が混ざる
- request / response struct が大量に増えて追えない
- 認証、例外、フォーマット変換が各 handler に散る
- `helpers.go` `common.go` が増えて責務が見えない

## shared に出してよいもの

- 共通 error response
- 認証済み session 取得
- 汎用フォーマッタ
- middleware

## shared に出しすぎない

- endpoint 固有の request/response
- 1 つの handler でしか使わない mapper
- 業務ロジックに見える helper

## 回答の出し方

1. 結論
2. 分割軸
3. 推奨ディレクトリ例
4. shared に出すもの / 出さないもの
