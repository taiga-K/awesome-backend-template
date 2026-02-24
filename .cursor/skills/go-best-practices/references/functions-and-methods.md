# 関数とメソッド

出典: [Effective Go](https://go.dev/doc/effective_go#functions), [Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Google Style Guide](https://google.github.io/styleguide/go/decisions)

## 目次
- [複数戻り値](#複数戻り値)
- [名前付き結果パラメータ](#名前付き結果パラメータ)
- [defer](#defer)
- [ポインタレシーバ vs バリューレシーバ](#ポインタレシーバ-vs-バリューレシーバ)
- [レシーバ型の選択](#レシーバ型の選択)
- [値渡し vs ポインタ渡し](#値渡し-vs-ポインタ渡し)
- [オプション構造体パターン](#オプション構造体パターン)
- [可変長オプションパターン](#可変長オプションパターン)

---

## 複数戻り値

Goの関数は複数の値を返すことができる。Cの帯域内エラー返却や引数のアドレス渡しによる変更を改善する。

```go
func (file *File) Write(b []byte) (n int, err error)
```

書き込みバイト数と、`n != len(b)` の場合の非nil `error` を返す。

### 実用例

```go
func nextInt(b []byte, i int) (int, int) {
    for ; i < len(b) && !isDigit(b[i]); i++ {
    }
    x := 0
    for ; i < len(b) && isDigit(b[i]); i++ {
        x = x*10 + int(b[i]) - '0'
    }
    return x, i
}
```

---

## 名前付き結果パラメータ

戻り値の「パラメータ」に名前を付けて通常の変数として使用できる:

```go
func ReadFull(r Reader, buf []byte) (n int, err error) {
    for len(buf) > 0 && err == nil {
        var nr int
        nr, err = r.Read(buf)
        n += nr
        buf = buf[nr:]
    }
    return
}
```

### いつ使うか

godocでの見え方を考慮する:

```go
// 悪い例 — godocで冗長
func (n *Node) Parent1() (node *Node) {}
func (n *Node) Parent2() (node *Node, err error) {}

// 良い例
func (n *Node) Parent1() *Node {}
func (n *Node) Parent2() (*Node, error) {}
```

同じ型の複数パラメータや、コンテキストから意味が不明確な場合に名前を付けると有用:

```go
// 不明確
func (f *Foo) Location() (float64, float64, error)

// 明確
// Locationはfの緯度と経度を返す。
// 負の値はそれぞれ南と西を意味する。
func (f *Foo) Location() (lat, long float64, err error)
```

### ネイキッドリターン

関数が数行の場合のみ許容。中規模以上の関数では戻り値を明示する。ネイキッドリターンのためだけに名前を付けない — ドキュメントの明確さが常に優先。

deferクロージャ内で結果パラメータを変更する必要がある場合の命名は常にOK。

---

## defer

`defer` は関数のリターン直前に呼び出される関数を予約する。リソースの確実な解放に有効。

```go
func Contents(filename string) (string, error) {
    f, err := os.Open(filename)
    if err != nil {
        return "", err
    }
    defer f.Close()  // 関数終了時にf.Closeが実行される

    var result []byte
    buf := make([]byte, 100)
    for {
        n, err := f.Read(buf[0:])
        result = append(result, buf[0:n]...)
        if err != nil {
            if err == io.EOF {
                break
            }
            return "", err  // ここでreturnしてもf.Closeが実行される
        }
    }
    return string(result), nil
}
```

### 利点
1. **解放忘れを防止** — 後からreturnパスが追加されても確実に閉じる
2. **開くコードの近くに閉じるコード** — 関数末尾に配置するより明確

### 引数の評価タイミング

defer実行文の引数はdefer時に評価される（呼び出し時ではない）:

```go
for i := 0; i < 5; i++ {
    defer fmt.Printf("%d ", i)
}
// 出力: 4 3 2 1 0 （LIFO順）
```

### 実行順序

遅延関数はLIFO（後入れ先出し）順で実行される。

---

## ポインタレシーバ vs バリューレシーバ

### ルール
- バリューメソッドはポインタと値の両方で呼び出し可能
- ポインタメソッドはポインタでのみ呼び出し可能

ポインタメソッドはレシーバを変更できるため。値で呼び出すとコピーへの変更は破棄される。

### 便利な例外

値がアドレス可能な場合、言語が自動的にアドレス演算子を挿入する:

```go
b.Write()    // 自動的に (&b).Write() に変換
```

### インターフェースの実装

```go
func (p *ByteSlice) Write(data []byte) (n int, err error) {
    slice := *p
    // ...
    *p = slice
    return len(data), nil
}

// *ByteSlice は io.Writer を満たす
var b ByteSlice
fmt.Fprintf(&b, "This hour has %d days\n", 7)
```

---

## レシーバ型の選択

迷ったらポインタを使う。以下はガイドライン:

### ポインタレシーバを使う場合
- メソッドがレシーバを変更する必要がある場合
- レシーバが `sync.Mutex` などの同期フィールドを含む構造体の場合（コピー回避）
- レシーバが大きな構造体や配列の場合（効率性）
- レシーバの要素にミューテーションする可能性のあるポインタが含まれる場合

### バリューレシーバを使う場合
- レシーバがmap、func、chanの場合はポインタを使わない
- レシーバがスライスでメソッドがリスライスや再割り当てをしない場合はポインタを使わない
- レシーバが小さな不変の構造体や基本型（`time.Time` のような型、`int`、`string`）の場合

### 重要なルール
- レシーバ型を混在させない。全てのメソッドでポインタか値のどちらかに統一する
- 迷ったらポインタレシーバを使う

---

## 値渡し vs ポインタ渡し

数バイトの節約のためだけにポインタを関数引数に渡さない。

```go
// 悪い例 — 不要なポインタ
func greet(name *string) string {
    return "Hello, " + *name
}

// 良い例 — 値を直接渡す
func greet(name string) string {
    return "Hello, " + name
}
```

### ルール
- 関数内で引数を `*x` としてのみ参照する場合、その引数はポインタであるべきでない
- `*string`、`*io.Reader` などは渡さない — 値自体が固定サイズで直接渡せる
- 大きな構造体やこれから大きくなる可能性のある構造体には適用しない

---

## オプション構造体パターン

引数を構造体に集約し、最後のパラメータとして渡す:

```go
type Options struct {
    Timeout    time.Duration
    MaxRetries int
    Logger     *log.Logger
}

func Connect(addr string, opts Options) (*Conn, error) { ... }

// 利用側
conn, err := Connect("localhost:8080", Options{
    Timeout:    30 * time.Second,
    MaxRetries: 3,
})
```

### 利点
- フィールド名で自己文書化
- ゼロ値フィールドを省略可能
- 呼び出し元間でオプションを共有可能
- フィールド単位のドキュメントが明確
- 呼び出し側に影響せず拡張可能

---

## 可変長オプションパターン

クロージャを返す関数をエクスポートする:

```go
type Option func(*config)

func WithTimeout(d time.Duration) Option {
    return func(c *config) { c.timeout = d }
}

func WithRetries(n int) Option {
    return func(c *config) { c.maxRetries = n }
}

func Connect(addr string, opts ...Option) (*Conn, error) {
    cfg := defaultConfig()
    for _, opt := range opts {
        opt(&cfg)
    }
    // ...
}

// 利用側
conn, err := Connect("localhost:8080",
    WithTimeout(30*time.Second),
    WithRetries(3),
)
```

### 利点
- 未設定時の呼び出し側スペースなし
- 値として共有・蓄積可能
- オプションが複数パラメータを受け取れる
- godocで名前付き型がオプションをグループ化

### 原則
オプションは存在を示すのではなくパラメータを受け取る（例: `FailFast(enable bool)` であって `EnableFailFast()` ではない）。順序に従って処理し、競合時は最後の引数が優先する。
