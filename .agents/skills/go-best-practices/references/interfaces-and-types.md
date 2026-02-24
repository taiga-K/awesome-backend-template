# インターフェースと型

出典: [Effective Go](https://go.dev/doc/effective_go#interfaces_and_types), [Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Google Style Guide](https://google.github.io/styleguide/go/decisions)

## 目次
- [インターフェース設計](#インターフェース設計)
- [埋め込み（Embedding）](#埋め込みembedding)
- [型アサーション](#型アサーション)
- [型変換](#型変換)
- [ジェネリクス](#ジェネリクス)
- [コピーに関する注意](#コピーに関する注意)
- [型エイリアスと型定義](#型エイリアスと型定義)

---

## インターフェース設計

### インターフェースは利用側パッケージに定義する

インターフェースは、それを使うパッケージに定義する。実装するパッケージではない:

```go
// 良い例 — 利用側パッケージ
package consumer

type Thinger interface { Thing() bool }

func Foo(t Thinger) string { ... }
```

```go
// 悪い例 — 実装側パッケージ
package producer

type Thinger interface { Thing() bool }

type defaultThinger struct{ ... }
func (t defaultThinger) Thing() bool { ... }
func NewThinger() Thinger { return defaultThinger{} }
```

代わりに具象型を返し、利用側にモックさせる:

```go
// 良い例
package producer

type Thinger struct{ ... }
func (t Thinger) Thing() bool { ... }
func NewThinger() Thinger { return Thinger{} }
```

### ルール
- 使う前にインターフェースを定義しない — 使用例なしでは必要性や適切なメソッドが分からない
- 「モックのため」に実装側でインターフェースを定義しない — 実装のパブリックAPIでテストする
- 具象型を返す — 新しいメソッドを実装に追加する際、大規模リファクタリングが不要
- メソッドが1-2個のインターフェースが一般的

### コンストラクタからインターフェースを返す場合

型がインターフェースを実装するためだけに存在し、それ以外に公開メソッドがない場合、型自体を公開する必要はない:

```go
// hash.Hash32 を crc32.NewIEEE と adler32.New が返す
// アルゴリズムの入れ替えはコンストラクタ呼び出しの変更のみ
```

### コンパイル時インターフェースチェック

型が特定のインターフェースを満たすことをコンパイル時に確認する:

```go
var _ json.Marshaler = (*RawMessage)(nil)
```

---

## 埋め込み（Embedding）

### インターフェースの埋め込み

```go
type ReadWriter interface {
    Reader
    Writer
}
```

`ReadWriter` は `Reader` が行うことと `Writer` が行うことの両方ができる。埋め込みインターフェースの和集合。

### 構造体の埋め込み

フィールド名を付けずに型を構造体にリスト化することで、埋め込み型のメソッドが外側の型に昇格する:

```go
type ReadWriter struct {
    *Reader  // *bufio.Reader
    *Writer  // *bufio.Writer
}
```

### サブクラスとの重要な違い

埋め込み型のメソッドが呼ばれたとき、レシーバは内側の型であり外側の型ではない。

### 実用的な埋め込み

```go
type Job struct {
    Command string
    *log.Logger
}

// Job は Print, Printf, Println などのメソッドを持つ
job.Println("starting now...")

// Logger フィールドにアクセス
job.Logger

// メソッドをリファイン
func (job *Job) Printf(format string, args ...interface{}) {
    job.Logger.Printf("%q: %s", job.Command, fmt.Sprintf(format, args...))
}
```

### 名前の衝突ルール
1. フィールドまたはメソッド `X` は、より深くネストされた `X` を隠蔽する
2. 同じネストレベルに同名が出現する場合は通常エラー（ただし、プログラム外で言及されなければOK）

---

## 型アサーション

### 基本形

```go
str := value.(string)  // 失敗するとパニック
```

### 安全な形式: カンマokイディオム

```go
str, ok := value.(string)
if ok {
    fmt.Printf("string value is: %q\n", str)
} else {
    fmt.Printf("value is not a string\n")
}
```

失敗した場合、`str` はstring型のゼロ値（空文字列）になる。

### 型スイッチ

型アサーションの変形。複数の型を効率的に判定:

```go
switch str := value.(type) {
case string:
    return str
case Stringer:
    return str.String()
}
```

---

## 型変換

同じ基底型を持つ型間の変換は新しい値を作成しない:

```go
type Sequence []int

func (s Sequence) String() string {
    s = s.Copy()
    sort.IntSlice(s).Sort()    // sort.IntSlice に変換
    return fmt.Sprint([]int(s)) // []int に変換
}
```

異なるメソッドセットにアクセスするために式の型を変換する。

---

## ジェネリクス

Go 1.18以降で使用可能。

### ルール
- ビジネス要件を満たす場合に使用する
- 早まって使用しない
- 不必要なポリモーフィズムのために使用しない
- ジェネリクスでDSLを作成しない — 確立されたエラー処理パターンに従う
- `any` は Go 1.18+ で `interface{}` のエイリアス。新しいコードでは `any` を優先

---

## コピーに関する注意

他パッケージの構造体をコピーする際は予期しないエイリアシングに注意する。

```go
// bytes.Buffer は []byte スライスを含む
// Buffer をコピーすると、コピーのスライスが元の配列をエイリアスする可能性がある
```

### ルール
- メソッドがポインタ型 `*T` に関連付けられている場合、`T` 型の値をコピーしない
- `sync.Mutex` や類似の同期フィールドを含む構造体はコピーしない
- `bytes.Buffer` を含む構造体をコピーする際は特に注意（内部スライスのエイリアシング）

---

## 型エイリアスと型定義

### 型定義（新しい型を作成）

```go
type T1 T2  // 新しい型 T1
```

### 型エイリアス（移行支援用）

```go
type T1 = T2  // T1 は T2 のエイリアス
```

型エイリアスは移行支援のためだけに使用する — まれなケース。通常は型定義を使う。
