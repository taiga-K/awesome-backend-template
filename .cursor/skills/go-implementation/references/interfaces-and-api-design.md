# インターフェースと API 設計

## いつ開くか

- interface を切るべきか、具体型のままにすべきか迷うとき
- `accept interfaces, return structs` をどう解釈するか確認したいとき
- `New`、export、cleanup、ゼロ値の責務を整理したいとき

## 基本原則

- interface は小さく、使う側の都合で定義する
- 入力は抽象を受けても、返り値は具体を基本にする
- API は誤用しにくく、後から変えやすい形にする

## 1. Small interfaces

- 1 メソッド interface を基本に考える
- 大きい interface は呼び出し側が不要な依存まで抱えやすい
- interface は合成できるので、最初から万能にしない

## 2. interface は使う側に置く

- 実装側で「この interface を実装します」と先回りしない
- 利用者が必要なメソッドだけを定義し、具象型を暗黙実装させる
- モックのためだけに大きな interface を export しない

## 3. Accept interfaces, return structs

- 引数は `io.Reader` のような最小の振る舞いに依存する
- 返り値は具体型を返し、利用者が必要なら自分で interface に受ける
- 返り値を interface にすると、実装の見通しと拡張余地を早く失いがち

## 4. コンストラクタ

- ゼロ値で安全に使えない型には `New` を用意する
- 主要な作り方が一つなら `New`、複数なら `NewXxx` を検討する
- 検証が必要なら `(*T, error)` を返す
- `Must*` は静的で起動時に確定する入力に限る

## 5. エクスポート最小化

- export は契約であり、安易に広げない
- 実装を隠したいなら非公開 concrete type と公開 interface の組み合わせを使う
- export された struct に `sync.Mutex` を埋め込んで API を漏らさない

## 6. ゼロ値とデフォルト

- 可能ならゼロ値で使える API にする
- nil logger を内部で `slog.Default()` に落とすような defaulting は有効
- ゼロ値で危険なら、ゼロ値利用を前提にしない API へ切り替える

## 7. cleanup

- リソース取得 API は `Close` か cleanup 関数の責務を明確にする
- `defer` で安全に後始末できる形を優先する
- cleanup 必須なら doc comment でも明示する

## 8. Functional Options

- デフォルトが自然で、オプションが増えうる API で検討する
- 1〜2個の引数しかないなら普通の引数の方が読みやすいことが多い
- 全利用者が必ず指定するなら option struct の方が素直なこともある

## レビュー観点

- interface が実装側に置かれていないか
- 引数が常に単一の concrete type なのに interface 化していないか
- 返り値 interface を安易に使っていないか
- `context.Context` を struct に保持していないか
- `New`、`Close`、default 値の責務が API から読めるか

## 関連

- ゼロ値やポインタ設計: [types-and-data-structures.md](types-and-data-structures.md)
- パッケージ境界と依存方向: [packages.md](packages.md)
- doc comment と Example: [comments.md](comments.md)
