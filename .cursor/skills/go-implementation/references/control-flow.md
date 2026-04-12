# 分岐とループ

## いつ開くか

- ネストが深く、正常系が見えにくいとき
- `switch` と `if` のどちらが自然か迷うとき
- `range`、`defer`、naked return の罠を避けたいとき

## 基本原則

- 正常系は左端に見えるようにする
- 異常系はガード節で早く抜ける
- Go の制御構文は少ないので、明示性を優先する

## 1. ネストを減らす

- `if err != nil { return err }` のようなガード節を使う
- `else` に正常系を押し込めない
- ループ内でも、先に `continue` で除外すると読みやすい
- 複雑な条件は名前付き bool か小関数へ切り出す

## 2. switch

- 長い `if` / `else if` 連鎖は `switch` を検討する
- Go の `switch` は自動で fallthrough しない
- `fallthrough` は本当に必要なときだけ使う
- `break` は `switch` だけを抜けるので、外側の `for` を抜けたいならラベル付きで書く

## 3. range ループの落とし穴

- `for _, v := range xs` の `v` は要素のコピーになりうる
- 要素を書き換えるなら `for i := range xs { xs[i] = ... }` にする
- 変数 capture を伴うクロージャでは、何を束縛しているか確認する

## 4. defer

- `Open` の直後に `defer Close()` を置くと後始末が追いやすい
- `defer` の引数は、その文に到達した時点で評価される
- 複数の `defer` は LIFO で実行される
- ループ内の `defer` は解放が遅れやすいので、別関数へ切り出す

## 5. Naked Return

- 長い関数では naked return を使わない
- 名前付き戻り値は `defer` で `err` を更新したいときなどに限る
- 迷ったら `return result, nil` のように明示する

## レビュー観点

- 正常系が `else` や深いネストの中に埋もれていないか
- `switch` で読みやすくできる箇所を `if` 連鎖で引き延ばしていないか
- `range` でコピーを書き換えているだけになっていないか
- ループ内 `defer` で FD や connection を溜め込まないか
- 長い関数で naked return を使っていないか

## 関連

- エラー処理を左端に置く考え方: [errors.md](errors.md)
- `select` や `context.Done()` の制御: [concurrency.md](concurrency.md)
