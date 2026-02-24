# 命名

出典: [Effective Go](https://go.dev/doc/effective_go#names), [Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Google Style Guide](https://google.github.io/styleguide/go/decisions#naming)

## 目次
- [MixedCaps](#mixedcaps)
- [パッケージ名](#パッケージ名)
- [レシーバ名](#レシーバ名)
- [インターフェース名](#インターフェース名)
- [ゲッター](#ゲッター)
- [変数名](#変数名)
- [定数](#定数)
- [頭字語（イニシャリズム）](#頭字語イニシャリズム)
- [重複の回避](#重複の回避)
- [関数名・メソッド名](#関数名メソッド名)

---

## MixedCaps

複数語の名前には `MixedCaps` または `mixedCaps` を使う。アンダースコアは使わない。

```go
// 良い例
maxLength
MaxLength
httpClient

// 悪い例
max_length
MAX_LENGTH
http_client
```

他言語の慣習を破る場合でもこのルールに従う。非公開定数は `maxLength` であり、`MAX_LENGTH` ではない。

アンダースコアの例外:
- 生成コードのみがインポートするパッケージ名
- `*_test.go` ファイル内のテスト/ベンチマーク/サンプル関数名
- OSやcgoと連携する低レベルライブラリ

---

## パッケージ名

パッケージ名は短く、簡潔で、小文字の単一語。アンダースコアやmixedCapsは使わない。

```go
// 良い例
package http
package tabwriter
package csv

// 悪い例
package httpUtil
package http_util
package HTTPUtil
```

### ルール
- パッケージ名がアクセサになる: `bytes.Buffer` であって `bytes.ByteBuffer` ではない
- 名前の重複を避ける: `chubby.File` であって `chubby.ChubbyFile` ではない
- 意味のない名前を避ける: `util`, `common`, `misc`, `api`, `types`, `interfaces`
- 複数語のパッケージは結合する: `tabwriter` であって `tab_writer` ではない
- 簡潔さを重視する — パッケージを使う全員がその名前を打つ
- 名前の衝突を恐れない — インポート側でリネーム可能

### 公開シンボルにおけるパッケージ名

全ての参照はパッケージ名付きで行われるため、識別子からパッケージ名を省略する:

```go
// 良い例 — 利用側は ring.New() と書く
package ring
func New() *Ring {}

// 悪い例 — 利用側は ring.NewRing() と書く
package ring
func NewRing() *Ring {}
```

---

## レシーバ名

型名の短い（1-2文字の）略称を使う。`this`、`self`、`me` は使わない。

```go
// 良い例
func (b *Buffer) Read(p []byte) (n int, err error) {}
func (c *Client) Do(req *Request) (*Response, error) {}

// 悪い例
func (this *Buffer) Read(p []byte) (n int, err error) {}
func (self *Client) Do(req *Request) (*Response, error) {}
func (buf *Buffer) Read(p []byte) (n int, err error) {}  // 長すぎる
```

### ルール
- レシーバは単なるパラメータ — それに応じた名前を付ける
- 一貫性を保つ: あるメソッドで `c` なら、別のメソッドで `cl` にしない
- メソッド引数ほど説明的である必要はない — 役割は自明
- 頻度が高いため簡潔さが許される

---

## インターフェース名

メソッドが1つのインターフェースは、メソッド名に `-er` サフィックスを付けて命名する:

```go
Reader    // Read メソッドを持つ
Writer    // Write メソッドを持つ
Formatter // Format メソッドを持つ
Stringer  // String メソッドを持つ
```

標準的なシグネチャを尊重する: `Read`, `Write`, `Close`, `Flush`, `String` には期待されるシグネチャがある。同じ意味を持つ場合にのみこれらの名前を使うこと。

---

## ゲッター

`Get` プレフィックスを省略する。フィールド名をゲッター名にする:

```go
// 良い例
func (o *Object) Owner() string    { return o.owner }
func (o *Object) SetOwner(s string) { o.owner = s }

// 悪い例
func (o *Object) GetOwner() string { return o.owner }
```

例外: 概念自体が「get」を使う場合のみ（例: HTTP GETリクエスト）。

---

## 変数名

小さなスコープには短い名前、大きなスコープには説明的な名前を使う。

```go
// 良い例 — 小さなスコープ
for i, v := range items {}
r := bytes.NewReader(data)

// 良い例 — 大きなスコープ
var userCount int
var primaryDatabase *sql.DB
```

### ルール
- 宣言箇所から離れるほど、名前はより説明的にすべき
- メソッドレシーバ: 1-2文字
- ループインデックス、リーダー: 1文字（`i`, `r`）
- グローバル変数: 説明的な名前
- 型情報を名前に含めない: `users` であって `userSlice` ではない、`count` であって `numCount` ではない
- 一般的な変数: `buf` は `*bytes.Buffer`、`err` は `error`、`ctx` は `context.Context`

### ゼロ値以外の初期化には `:=` を優先

```go
// 良い例
i := 42
s := "hello"

// あまり慣用的でない
var i = 42
var s = "hello"
```

ゼロ値宣言で空の使用可能な値を表す場合は `var` を使う:

```go
var coords Point       // ゼロ値が有意味
var buf bytes.Buffer   // そのまま使用可能
```

---

## 定数

他の名前と同様に `MixedCaps` を使う。値ではなく役割に基づいて命名する。

```go
// 良い例
const maxItems = 100
const DefaultPort = 8080

// 悪い例
const MAX_ITEMS = 100
const KMaxItems = 100
```

### iotaによる列挙

```go
type ByteSize float64

const (
    _           = iota // 最初の値を無視
    KB ByteSize = 1 << (10 * iota)
    MB
    GB
    TB
    PB
    EB
)
```

---

## 頭字語（イニシャリズム）

頭字語やアクロニムは大文字・小文字を一貫させる。`URL` は `URL` または `url` であり、`Url` にはしない。

```go
// 良い例
ServeHTTP
xmlHTTPRequest
XMLHTTPRequest
appID
urlPony
URLPony

// 悪い例
ServeHttp
XmlHttpRequest
appId
```

「identifier」の略としての `ID` は常に `ID`（`Id` ではない）。

プロトコルバッファの生成コードはこのルールの例外。

---

## 重複の回避

### パッケージ名 vs シンボル名

公開シンボルにパッケージ名を繰り返さない:

```go
// 良い例 — widget.New(), widget.Parse()
package widget
func New() *Widget {}
func Parse(s string) (*Widget, error) {}

// 悪い例 — widget.NewWidget(), widget.ParseWidget()
package widget
func NewWidget() *Widget {}
func ParseWidget(s string) (*Widget, error) {}
```

### 変数名 vs 型名

変数名に型名を含めない:

```go
// 良い例
var users []*User
var nameToUser map[string]*User

// 悪い例
var userSlice []*User
var userMap map[string]*User
```

### 外部コンテキスト

呼び出し元から得られるコンテキストを重複させない:

```go
// 良い例 — dbパッケージ内
func (db *DB) UserCount() int {}

// 悪い例 — dbパッケージ内
func (db *DB) DBUserCount() int {}
```

---

## 関数名・メソッド名

### 命名パターン
- **名詞的** — 値を返す関数: `time.Now()`, `os.Hostname()`
- **動詞的** — アクションを実行する関数: `fmt.Print()`, `sort.Sort()`
- **型サフィックス** — 型で異なるオーバーロード関数: `ParseInt()`, `ParseInt64()`

### コンテキストの繰り返しを避ける
- メソッド名にレシーバ型を繰り返さない: `Config` レシーバでは `WriteTo()` であり `WriteConfigTo()` ではない
- 使用時に自明な場合、パラメータ名を関数名に繰り返さない
- 戻り値の型名を関数名に繰り返さない
