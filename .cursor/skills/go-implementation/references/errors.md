# エラー

## いつ開くか

- `panic` と `error` の境界に迷うとき
- sentinel error / error type / opaque error の選び分けをしたいとき
- `%w`、`errors.Is`、`errors.As` をどう使うべきか確認したいとき

## 基本原則

- **Errors are values**
- エラー処理は一度だけ行う
- 呼び出し側が区別しないなら opaque error を基本にする
- ライブラリや中間層は、まず wrap して返すことを考える

## 1. エラーは値として扱う

- `if err != nil { return ... }` のあとに正常系が続く形を保つ
- ループ中にエラー処理を散らすより、`Scanner` のように最後に `Err()` を見る API を好む
- 正常系を左端に置く考え方は、制御フローの指針とつながる

## 2. 3つのエラー表現

- sentinel error: 呼び出し側が特定の失敗を区別したいとき
- error type: 呼び出し側が追加情報を取り出したいとき
- opaque error: 呼び出し側が `err != nil` だけ見ればよいとき
- デフォルトは opaque error に寄せ、公開契約を広げ過ぎない

## 3. 判定と wrap

- `errors.Is` / `errors.As` を使う
- `err == ErrXxx` や型アサーション直書きは wrap に弱い
- `fmt.Errorf("read config: %w", err)` のように `%w` で文脈を足す
- `%v` を使うと unwrap できなくなる

```go
if err != nil {
	return fmt.Errorf("read %s: %w", path, err)
}
```

## 4. nil interface の罠

- `var err *ValidationError` を `error` として返すと non-nil になりうる
- エラーがないなら明示的に `return nil` する

## 5. エラー処理は一度だけ

- `log + return` を多層で繰り返さない
- 下位層では wrap して返し、最上位でログやレスポンス変換を行う
- 例外は、その場で完全に処理を閉じるケースだけ

## 6. panic の境界

- 通常の失敗は `panic` ではなく `error` で返す
- ライブラリやリクエスト処理で `panic` を使わない
- `Must*` は起動時に確定している静的入力でのみ検討する
- `recover` は同じ goroutine でしか効かない

## 7. エラーを存在しないものとして定義する

- idempotent delete のように、失敗として扱わない設計が有効なことがある
- ただし「無視してよい失敗」と「握り潰してはいけない失敗」は分ける
- デフォルト値で誤魔化すより、契約として明示する

## レビュー観点

- `panic` や `log.Fatal` が通常経路に混ざっていないか
- `err.Error()` の文字列比較をしていないか
- `%v` で元エラーを潰していないか
- 下位層で `log + return` の二重処理をしていないか
- 呼び出し側が不要なエラー表現まで公開していないか

## 関連

- 左端に正常系を置く制御フロー: [control-flow.md](control-flow.md)
- doc comment や Example で API 契約を書く: [comments.md](comments.md)
