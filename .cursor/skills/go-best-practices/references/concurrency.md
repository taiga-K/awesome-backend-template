# 並行処理

出典: [Effective Go](https://go.dev/doc/effective_go#concurrency), [Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Google Style Guide](https://google.github.io/styleguide/go/decisions)

## 目次
- [通信による共有](#通信による共有)
- [ゴルーチン](#ゴルーチン)
- [チャネル](#チャネル)
- [チャネルのチャネル](#チャネルのチャネル)
- [並列化](#並列化)
- [ゴルーチンの生存期間](#ゴルーチンの生存期間)
- [同期関数の優先](#同期関数の優先)
- [selectパターン](#selectパターン)

---

## 通信による共有

> メモリの共有によって通信するのではなく、通信によってメモリを共有せよ。

Goでは共有値はチャネルを通じて受け渡され、実際には別々の実行スレッドが同時にアクティブに共有することはない。任意の時点で値にアクセスできるのは1つのゴルーチンのみ。この設計によりデータ競合は発生しない。

このアプローチは過度に適用すべきではない。参照カウントはミューテックスで保護された整数変数で行うのが最適な場合もある。ただし高レベルのアプローチとしては、チャネルを使ったアクセス制御が明確で正しいプログラムを書きやすくする。

---

## ゴルーチン

ゴルーチンは同じアドレス空間内の他のゴルーチンと並行して実行される関数。軽量で、スタックスペースの割り当て以上のコストはほぼない。

### 特性
- スタックは小さく開始し、必要に応じてヒープストレージの確保/解放で成長
- 複数のOSスレッド上に多重化される
- 1つがブロック（I/O待ちなど）しても他は実行を継続
- スレッド作成と管理の複雑さを隠蔽

### ゴルーチンの起動

`go` キーワードで関数またはメソッド呼び出しの前に付ける:

```go
go list.Sort()  // list.Sortを並行実行。完了を待たない
```

関数リテラルでの使用:

```go
func Announce(message string, delay time.Duration) {
    go func() {
        time.Sleep(delay)
        fmt.Println(message)
    }()  // 括弧に注意 — 関数を呼び出す必要がある
}
```

関数リテラルはクロージャ — 参照される変数は関数がアクティブな限り存続する。

---

## チャネル

`make` で割り当てる。結果の値は基底データ構造への参照として機能する:

```go
ci := make(chan int)            // バッファなし整数チャネル
cj := make(chan int, 0)         // バッファなし整数チャネル
cs := make(chan *os.File, 100)  // バッファ付きFileポインタチャネル
```

### バッファなしチャネル

通信と同期を組み合わせる — 2つのゴルーチンが既知の状態にあることを保証:

```go
c := make(chan int)
go func() {
    list.Sort()
    c <- 1  // シグナルを送信。値は重要でない
}()
doSomethingForAWhile()
<-c   // ソート完了を待つ。送信値は破棄
```

### バッファ付きチャネルをセマフォとして使用

スループットを制限する:

```go
var sem = make(chan int, MaxOutstanding)

func handle(r *Request) {
    sem <- 1    // アクティブキューが空くのを待つ
    process(r)  // 時間がかかる可能性がある
    <-sem       // 完了。次のリクエストを許可
}

func Serve(queue chan *Request) {
    for {
        req := <-queue
        go handle(req)
    }
}
```

### 固定数のワーカー

リクエストチャネルから読み取る固定数のゴルーチンを起動する方が良いアプローチ:

```go
func handle(queue chan *Request) {
    for r := range queue {
        process(r)
    }
}

func Serve(clientRequests chan *Request, quit chan bool) {
    for i := 0; i < MaxOutstanding; i++ {
        go handle(clientRequests)
    }
    <-quit  // 終了指示を待つ
}
```

---

## チャネルのチャネル

チャネルはファーストクラスの値 — 他の値と同様に割り当てや受け渡しが可能。

クライアントが応答パスを提供するパターン:

```go
type Request struct {
    args        []int
    f           func([]int) int
    resultChan  chan int
}

// クライアント側
request := &Request{[]int{3, 4, 5}, sum, make(chan int)}
clientRequests <- request
fmt.Printf("answer: %d\n", <-request.resultChan)

// サーバー側
func handle(queue chan *Request) {
    for req := range queue {
        req.resultChan <- req.f(req.args)
    }
}
```

レート制限された並列・非ブロッキングRPCシステムのフレームワーク — ミューテックスなし。

---

## 並列化

計算を独立した部分に分割して複数CPUコアで並列実行:

```go
type Vector []float64

func (v Vector) DoSome(i, n int, u Vector, c chan int) {
    for ; i < n; i++ {
        v[i] += u.Op(v[i])
    }
    c <- 1  // この部分の完了を通知
}

func (v Vector) DoAll(u Vector) {
    c := make(chan int, runtime.NumCPU())
    for i := 0; i < runtime.NumCPU(); i++ {
        go v.DoSome(i*len(v)/runtime.NumCPU(), (i+1)*len(v)/runtime.NumCPU(), u, c)
    }
    for i := 0; i < runtime.NumCPU(); i++ {
        <-c  // 1つのタスクの完了を待つ
    }
}
```

### 並行性と並列性の違い
- **並行性（Concurrency）**: プログラムを独立して実行するコンポーネントとして構造化すること
- **並列性（Parallelism）**: 複数CPUで効率のため計算を並列実行すること

Goは並行言語であり、並列言語ではない。全ての並列化問題がGoのモデルに適合するわけではない。

---

## ゴルーチンの生存期間

ゴルーチンを起動する際は、いつ（または）終了するかを明確にする。

### 問題
- チャネルの送受信でブロックされたゴルーチンはリークする — GCはチャネルが到達不能でもゴルーチンを終了しない
- リークしなくても、不要になった実行中のゴルーチンは問題を引き起こす:
  - 閉じたチャネルへの送信はパニック
  - 使用中の入力を「結果が不要になった後」に変更するとデータ競合
  - 任意の長時間実行は予測不能なメモリ使用量

### ルール
- 並行コードをゴルーチンの生存期間が自明なほど単純に保つ
- それが不可能な場合、いつ・なぜ終了するかをドキュメントする
- `context.Context` と `sync.WaitGroup` を使用してゴルーチンの終了を管理
- 終了条件を知らずにゴルーチンを起動しない

---

## 同期関数の優先

結果を直接返すか、コールバック/チャネル操作をreturn前に完了する同期関数を優先する。

```go
// 良い例 — 同期関数
func Process(data []byte) (Result, error) {
    // データを処理して結果を返す
    return result, nil
}

// 避ける — 非同期関数
func Process(data []byte, callback func(Result, error)) {
    go func() {
        // ...
        callback(result, nil)
    }()
}
```

### 理由
- ゴルーチンを呼び出し内に局所化し、生存期間の推論やリーク・データ競合の回避が容易
- テストが容易 — 入力を渡して出力を確認するだけ（ポーリングや同期不要）
- 呼び出し側がさらに並行性を必要とする場合、別のゴルーチンから呼び出すことで簡単に追加可能
- 呼び出し側で不要な並行性を除去するのは困難 — 時に不可能

---

## selectパターン

### リーキーバケット（フリーリスト）

バッファ付きチャネルとGCでブックキーピングを行う:

```go
var freeList = make(chan *Buffer, 100)
var serverChan = make(chan *Buffer)

func client() {
    for {
        var b *Buffer
        select {
        case b = <-freeList:
            // 取得。何もする必要なし
        default:
            // 空きなし、新規割り当て
            b = new(Buffer)
        }
        load(b)
        serverChan <- b
    }
}

func server() {
    for {
        b := <-serverChan
        process(b)
        select {
        case freeList <- b:
            // フリーリストに返却
        default:
            // フリーリストが満杯。GCに回収させる
        }
    }
}
```

`select` の `default` 句は他のcaseが準備できていない場合に実行される — selectがブロックしないことを保証。

### crypto/rand

鍵の生成には `math/rand` や `math/rand/v2` ではなく `crypto/rand` を使う:

```go
import "crypto/rand"

func Key() string {
    return rand.Text()
}
```

`math/rand` は `Time.Nanoseconds()` でシードされたわずかなエントロピーしかない。
