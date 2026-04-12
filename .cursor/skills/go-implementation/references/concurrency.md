# 並行処理

## いつ開くか

- goroutine や channel を入れるべきか迷うとき
- `context`、`select`、`sync` の役割分担を整理したいとき
- goroutine リークや停止条件の漏れをレビューしたいとき

## 基本原則

- 並行性は構造、並列性は実行形態である
- goroutine を起動したら終了条件と所有者を決める
- channel は協調、mutex は共有状態の保護に向く

## 1. Concurrency と Parallelism

- 並行処理は「同時に進む可能性を持つ構造」であり、必ずしも高速化ではない
- まず同期関数として設計し、必要なら呼び出し側が `go` する
- fire-and-forget は避け、完了待ちやキャンセルを設計に含める

## 2. channel

- デフォルトは非バッファから考える
- バッファサイズには理由を持つ
- 方向付き channel で意図を型に載せる
- close は送信側の責務であり、複数送信者がいるなら一箇所に寄せる

## 3. select

- 複数の待ち合わせを扱うときは `select` を使う
- タイムアウトやキャンセルは `ctx.Done()` と組み合わせる
- ループ内 `default` は busy loop を作りやすい
- `time.Sleep` だけではキャンセルできない待機になる

## 4. sync

- 単純な共有状態保護なら `sync.Mutex` をまず考える
- `Mutex` を埋め込んで API へ漏らさない
- 同期オブジェクトを値コピーしない
- エラー伝播や並行数制御が必要なら `errgroup` も有力

## 5. context

- `context.Context` は呼び出しチェーンの第1引数で渡す
- struct フィールドに保持しない
- `WithCancel` / `WithTimeout` を使ったら `cancel` を忘れない
- `context.Value` はリクエストスコープのメタデータに限る

## 6. goroutine リークの防止

- 終了条件のない goroutine を起動しない
- 停止要求と完了待ちの両方を考える
- `init()` でバックグラウンド goroutine を始めない
- `go test -race` を継続的に使う

## レビュー観点

- `go` だけがあり、待ち合わせ・キャンセル・エラー伝播がないか
- channel close の責務が曖昧でないか
- `select` が busy loop や uninterruptible sleep を作っていないか
- `context` を保持したり、下位へ渡し忘れたりしていないか
- goroutine の停止条件と所有者が読み取れるか

## 関連

- `select` 以外の制御フロー: [control-flow.md](control-flow.md)
- mutex を含む型やコピー禁止型: [types-and-data-structures.md](types-and-data-structures.md)
- 並行安全性を doc に書く話: [comments.md](comments.md)
