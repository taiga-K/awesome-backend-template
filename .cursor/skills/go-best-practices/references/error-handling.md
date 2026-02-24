# エラー処理

出典: [Effective Go](https://go.dev/doc/effective_go#errors), [Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Google Style Guide](https://google.github.io/styleguide/go/decisions), [Google Best Practices](https://google.github.io/styleguide/go/best-practices)

## 目次
- [errorインターフェース](#errorインターフェース)
- [エラー文字列](#エラー文字列)
- [エラーの処理](#エラーの処理)
- [帯域内エラー](#帯域内エラー)
- [エラーのラッピング（%v vs %w）](#エラーのラッピングv-vs-w)
- [センチネルエラーとカスタムエラー型](#センチネルエラーとカスタムエラー型)
- [Don't Panic](#dont-panic)
- [Recover](#recover)
- [エラーログ](#エラーログ)

---

## errorインターフェース

Goではエラーは組み込みの `error` インターフェースを実装する値:

```go
type error interface {
    Error() string
}
```

### リッチなエラー型

ライブラリ作成者はこのインターフェースをより豊富なモデルで実装できる:

```go
type PathError struct {
    Op   string    // "open", "unlink" など
    Path string    // 関連するファイルパス
    Err  error     // システムコールが返したエラー
}

func (e *PathError) Error() string {
    return e.Op + " " + e.Path + ": " + e.Err.Error()
}
```

出力例: `open /etc/passwx: no such file or directory`

### ルール
- 公開関数は `error` 型を返す（具象エラー型ではない）— nilインターフェースバグを回避
- `nil` は成功を示す

---

## エラー文字列

エラー文字列は小文字で始め（固有名詞やアクロニムで始まる場合を除く）、句読点で終わらない:

```go
// 良い例
fmt.Errorf("something bad")

// 悪い例
fmt.Errorf("Something bad")   // 先頭大文字
fmt.Errorf("something bad.")  // 末尾句読点
```

理由: 通常、他のコンテキストに続けて出力されるため:

```go
log.Printf("Reading %s: %v", filename, err)
// "Reading foo.txt: something bad" — 良い
// "Reading foo.txt: Something bad" — 不自然な大文字
```

この規則はログには適用されない（ログは暗黙的に行指向であり他のメッセージと結合されない）。

---

## エラーの処理

エラーを `_` で破棄しない。関数がエラーを返す場合、必ず確認して処理する:

```go
// 悪い例 — パスが存在しないとクラッシュ
fi, _ := os.Stat(path)
if fi.IsDir() {
    fmt.Printf("%s is a directory\n", path)
}

// 良い例
fi, err := os.Stat(path)
if err != nil {
    // エラーを処理
    return err
}
```

### 処理の選択肢
1. エラーをすぐに処理する
2. エラーを呼び出し元に返す
3. 真に例外的な状況でのみ `log.Fatal` や `panic`

意図的にエラーを破棄する場合はコメントする。

---

## 帯域内エラー

-1やnullなどのセンチネル値でエラーを示す代わりに、追加の戻り値を使う:

```go
// 悪い例 — 帯域内エラー
func Lookup(key string) string  // "" がエラーを示す

// 良い例 — 別の戻り値
func Lookup(key string) (value string, ok bool)
```

これにより呼び出し側の誤用を防ぐ:

```go
Parse(Lookup(key))  // 帯域内エラーの場合、コンパイル可能だがバグ

value, ok := Lookup(key)
if !ok {
    return fmt.Errorf("no value for %q", key)
}
return Parse(value)  // 安全
```

nil、""、0、-1 が関数の有効な結果である場合は、これらを返して問題ない。

---

## エラーのラッピング（%v vs %w）

### %v を使う場合
- 単純な注釈
- ログ出力
- 新しいエラーメッセージの作成
- システム境界でのエラー変換

### %w を使う場合
- 呼び出し側が `errors.Is` や `errors.As` で元のエラーを検査する必要がある場合

```go
// %v — エラーチェーンを切断
return fmt.Errorf("failed to load config: %v", err)

// %w — エラーチェーンを維持
return fmt.Errorf("failed to load config: %w", err)
```

### 配置ルール
`%w` はエラー文字列の末尾に `[...]: %w` の形式で配置することを推奨。一貫したエラーチェーン出力のため。

### 情報の追加
- 元のエラーに既にある情報を重複させない
- コンテキスト固有の意味を提供する（例: `os.Open` エラーに対して「launch codes unavailable」は価値がある）
- 単に失敗を示すための注釈は不要 — エラーの存在自体が十分

---

## センチネルエラーとカスタムエラー型

### センチネル値

グローバルでパラメータなしのエラー値。`==` や `errors.Is` で比較:

```go
var ErrNotFound = errors.New("not found")

if errors.Is(err, ErrNotFound) {
    // 処理
}
```

### カスタムエラー型

エラーコードや詳細を含む構造体:

```go
type PathError struct {
    Op   string
    Path string
    Err  error
}
```

### 型スイッチによるエラー検査

```go
for try := 0; try < 2; try++ {
    file, err = os.Create(filename)
    if err == nil {
        return
    }
    if e, ok := err.(*os.PathError); ok && e.Err == syscall.ENOSPC {
        deleteTempFiles()  // スペースを回復
        continue
    }
    return
}
```

### エラー文字列の原点

可能な場合、エラー文字列は発生元を示すプレフィックスを含むべき:

```go
// imageパッケージ内
return fmt.Errorf("image: unknown format")
```

---

## Don't Panic

通常のエラー処理に `panic` を使わない。`error` と複数戻り値を使う。

```go
// 悪い例
func MustParse(s string) *Config {
    cfg, err := Parse(s)
    if err != nil {
        panic(err)  // 通常のエラーでpanic
    }
    return cfg
}

// 良い例
func Parse(s string) (*Config, error) {
    // ...
    return cfg, nil
}
```

### panicが許容される場合
- 初期化時 — ライブラリが自身のセットアップに失敗した場合
- プログラムが続行できない真に回復不能な状態
- APIの誤用（`reflect`、配列境界チェック等 — テストで捕捉されるべき）
- パッケージ内部で `recover` と対にして使う場合（パッケージ外に漏れない）

### Must関数の命名規則
- パニックするセットアップヘルパーは `MustXYZ` と命名
- 初期化時のみ呼び出す（ユーザー入力に対しては使わない）
- テストヘルパーは `mustXYZ`（非公開）で `t.Fatal` を使用可

```go
func init() {
    if user == "" {
        panic("no value for $USER")
    }
}
```

---

## Recover

`panic` が呼ばれると、現在の関数の実行を停止しゴルーチンのスタックを巻き戻す。巻き戻し中にdefer関数が実行される。

`recover` は巻き戻しを停止し、`panic` に渡された引数を返す。defer関数内でのみ有用。

### サーバーでの活用例

失敗するゴルーチンを他のゴルーチンを殺さずにシャットダウンする:

```go
func server(workChan <-chan *Work) {
    for work := range workChan {
        go safelyDo(work)
    }
}

func safelyDo(work *Work) {
    defer func() {
        if err := recover(); err != nil {
            log.Println("work failed:", err)
        }
    }()
    do(work)
}
```

### 注意
- panicからの復帰は破損した状態を伝播させる可能性がある
- `net/http` サーバーのパニック復帰は歴史的な間違いと見なされている

---

## エラーログ

### ルール
- ログメッセージは何が問題かを表現し、診断に役立つようにする
- 重複を避ける: 返されるエラーをログに記録するかは呼び出し側に任せる
- ログ内のPII（個人情報）に注意
- `log.Error` は控えめに — フラッシュを引き起こしパフォーマンスに影響
- エラーレベルのログはアクション可能なメッセージに限る

### プログラム初期化

初期化エラーは `main` に伝播させ、`main` がアクション可能なメッセージで `log.Exit` を呼ぶ。スタックトレースを含む `log.Fatal` は避ける。
