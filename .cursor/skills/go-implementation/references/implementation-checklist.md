# Go 実装チェックリスト

## 使い方

- 実装前に API と責務を決める
- 実装中に命名、エラー、型、`context` の判断を確認する
- 実装後にテスト、doc comment、リーク有無を見直す

詳細な根拠や例は [../SKILL.md](../SKILL.md) の追加資料から該当トピックを開く。

## 1. 命名

- スコープが狭い場所だけ短い名前を使う
- 型ラベルの重複や他言語風の命名を避ける
- 頭字語や getter の扱いは Go 慣習に寄せる

## 2. エラー

- エラーは `panic` ではなく値として返す
- 呼び出し側が区別しないなら opaque error を基本にする
- 文脈追加は `%w` を使い、判定は `errors.Is` / `errors.As` を使う
- エラー処理は一度だけ行う
- 下位層では `log + return` を避け、最上位でログやレスポンス変換を行う
- `error` を返すなら、nil pointer を interface に詰めて返さない

## 3. 制御フロー

- 正常系を左端に置き、エラーは早期 return する
- 深いネストよりガード節を優先する
- `switch` が自然なら `if` 連鎖にしない
- `range` で値コピーが起きることを意識する
- `defer` は後始末や commit/rollback の責務が明確な場面で使う
- 長い関数で naked return を使わない

## 4. 型とデータ構造

- ゼロ値で安全に使える型を優先する
- pointer receiver / value receiver は一貫した意図で選ぶ
- `var` と `:=` は初期値の有無と可読性で使い分ける
- `slice` / `map` の nil と empty の意味差を意識する
- enum 的な値は意味のある独自型と定数群で表し、連番が自然なときは `iota` を使う

## 5. interface と API 設計

- interface は利用側で必要になってから導入する
- 小さい interface を優先し、大きな万能 interface を避ける
- 入力で interface を受け、返り値は struct や具体型を返す
- `New` を付けるのはゼロ値だけでは不十分な初期化が必要なとき
- export は最小限に保つ
- 可能ならゼロ値で利用できる API にする
- resource を開く型は `Close` や cleanup 関数の責務を明確にする

## 6. パッケージ

- パッケージ名は短く役割が分かるものにする
- `common` `util` `base` の逃がし先を増やさない
- `internal` と `cmd` の責務を分ける
- 循環依存を避け、依存方向を明示する
- `init()` とグローバル状態はできるだけ避ける
- 依存は最小に保ち、外部パッケージ追加には理由を持つ

## 7. テスト

- まず table-driven test を検討する
- テスト名は仕様が読める形にする
- 失敗メッセージに入力値、期待値、実際値を含める
- 外部境界をどう切るかを先に決める
- バグ修正時は再発防止テストを追加する
- Example が有効な公開 API には `example_test.go` を検討する

## 8. コメント

- export された名前には doc comment を付ける
- doc comment はシンボル名で始まる完全な文にする
- 利用者が知るべき振る舞い、副作用、制約を書く
- 実装詳細は doc comment ではなく関数本体の近くに書く
- goroutine-safe かどうか、`Close` が必要かどうかはコメントで明示する

## 9. 並行処理

- goroutine を始めたら終了条件と所有者を決める
- `context.Context` を上位から下位へ伝播させる
- cancel されてもブロックし続ける send/receive を作らない
- channel は同期手段であってデータ構造ではないと意識する
- `sync.Mutex` で十分な場面で複雑な channel 構成にしない
- goroutine リーク、timer leak、close 忘れを疑う

## 実装後の最終確認

- API が誤用しにくいか
- エラーに十分な文脈があるか
- 公開シンボルに doc comment があるか
- 並行処理にキャンセル経路があるか
- 差分に見合うテストがあるか
