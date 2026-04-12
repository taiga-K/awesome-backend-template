# ネーミング

## いつ開くか

- 名前がしっくり来ないが、何を基準に直すべきか迷うとき
- `GetXxx`、`IReader`、`HttpClient` のような他言語流の命名が混ざるとき
- コメントで意味を補っていて、名前自体が弱いと感じるとき

## 基本原則

- 良い名前は **一貫していて、短く、正確** である
- スコープが狭いほど短く、広いほど説明的にする
- 型や文脈で分かる情報を名前へ重ねない
- 名前は **What** を表し、**Why** はコメントで補う

## 1. 短さはスコープで決める

- ループ変数や数行のローカル変数は `i` `v` `n` `err` `ctx` でよい
- パッケージ変数や広いスコープでは、役割が読める名にする
- 同じ型の値を区別するときは、型名ではなく意味で区別する

```go
var globalConfig *Config

func Copy(dst Writer, src Reader) error
```

## 2. 型情報を名前に入れない

- `usersMap` `configStruct` `userList` のような命名を避ける
- 将来 `map` が `slice` に変わっても意味が壊れない名前にする
- `int64` のように型だけでは意味が弱いときは、`sec` `nsec` のように名前で補う

## 3. 一貫性を優先する

- 同じ概念に別名を付けない
- レシーバ名は同じ型で統一する
- コミュニティ慣習に寄せる: `ctx` `err` `r` `w` `buf`

## 4. MixedCaps と頭字語

- 識別子は `camelCase` / `PascalCase` を使う
- `HTTP` `URL` `ID` のような頭字語はまとめて大文字にする
- 定数も `ALL_CAPS` ではなく通常の Go 識別子に寄せる

```go
type HTTPClient struct{}

func ParseURL(s string) (*URL, error)
```

## 5. Getter と interface 名

- 単なる参照メソッドに `Get` を付けない
- 単一メソッド interface は `Reader` `Writer` のように `-er` 系を基本にする
- `IReader` `WriterInterface` のような命名は避ける
- 複数メソッド interface は、そのものが何かを表す名詞にする

## 6. コメントとの境界

- コメントがないと意味が分からない名前なら、まず名前を直す
- 名前で表せることを doc comment に逃がさない
- 「なぜそうするか」はコメントの担当であり、名前で無理に表さない

## 7. gofmt との境界

- `gofmt` や `goimports` は空白や import を揃える
- 命名の良し悪しは自動整形では解決しない
- 書式の議論で終わらせず、名前そのものの設計を見る

## レビュー観点

- パッケージ名と型名が重複して stutter していないか
- スコープの広い変数が1文字名になっていないか
- 型ラベルでしか区別できない命名になっていないか
- `HttpClient` / `ParseUrl` のように頭字語が崩れていないか
- `GetXxx()` や `IReader` のような他言語風が混ざっていないか

## 関連

- エラー値や `ErrXxx` / `XxxError` の命名: [errors.md](errors.md)
- doc comment の詳細: [comments.md](comments.md)
