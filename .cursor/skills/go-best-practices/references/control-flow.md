# 制御フロー

出典: [Effective Go](https://go.dev/doc/effective_go#control-structures), [Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Google Style Decisions](https://google.github.io/styleguide/go/decisions)

## 目次
- [if文](#if文)
- [for文](#for文)
- [switch文](#switch文)
- [エラーフローのインデント](#エラーフローのインデント)

---

## if文

### 初期化文

`if` は初期化文を受け取り、ローカル変数を設定できる:

```go
if err := file.Chmod(0664); err != nil {
    log.Print(err)
    return err
}
```

### 不要なelseを省略

本体が `break`, `continue`, `goto`, `return` で終わる場合、`else` を省略する:

```go
// 良い例
f, err := os.Open(name)
if err != nil {
    return err
}
codeUsing(f)

// 悪い例 — 不要なelse
f, err := os.Open(name)
if err != nil {
    return err
} else {
    codeUsing(f)
}
```

### 複数のエラーチェック

エラーチェックを連鎖させ、正常フローをページの下方向に流す:

```go
f, err := os.Open(name)
if err != nil {
    return err
}
d, err := f.Stat()
if err != nil {
    f.Close()
    return err
}
codeUsing(f, d)
```

### if文を改行しない

条件が長すぎる場合は、ブール値のオペランドをローカル変数に抽出する:

```go
// 悪い例
if longCondition1 && longCondition2 &&
    longCondition3 {
    doSomething()
}

// 良い例
ready := longCondition1 && longCondition2 && longCondition3
if ready {
    doSomething()
}
```

---

## for文

Goは `for` と `while` を統一。`do-while` はない:

```go
for init; condition; post {}  // C言語スタイルのfor
for condition {}              // while相当
for {}                        // 無限ループ
```

### range

配列、スライス、文字列、マップ、チャネルに対してループ:

```go
// キーと値
for key, value := range oldMap {
    newMap[key] = value
}

// キーのみ
for key := range m {
    if key.expired() {
        delete(m, key)
    }
}

// 値のみ（キーを破棄）
for _, value := range array {
    sum += value
}
```

### 文字列のrange

文字列の `range` はバイトではなくUnicodeコードポイント（ルーン）を反復する:

```go
for pos, char := range "Hello, 世界" {
    fmt.Printf("文字 %c はバイト位置 %d\n", char, pos)
}
```

### forでの並行代入

Goにはコンマ演算子がない。並行代入を使う:

```go
// スライスを反転
for i, j := 0, len(a)-1; i < j; i, j = i+1, j-1 {
    a[i], a[j] = a[j], a[i]
}
```

### `:=` による再宣言

`:=` は同じスコープ内で `err` の再利用を許可する（少なくとも1つの新しい変数が宣言される場合）:

```go
f, err := os.Open(name)
d, err := f.Stat()  // errは再代入（再宣言ではない）
```

---

## switch文

### 一般形

GoのswitchはC言語より柔軟:
- 式は定数や整数でなくてもよい
- caseは上から下へ評価され、一致したら停止
- 自動フォールスルーなし
- 複数一致にはカンマ区切り:

```go
func shouldEscape(c byte) bool {
    switch c {
    case ' ', '?', '&', '=', '#', '+', '%':
        return true
    }
    return false
}
```

### trueに対するswitch

式なしの switch は `switch true {}` — きれいなif-else-ifチェーン:

```go
func classify(c byte) string {
    switch {
    case '0' <= c && c <= '9':
        return "digit"
    case 'a' <= c && c <= 'z':
        return "lower"
    case 'A' <= c && c <= 'Z':
        return "upper"
    }
    return "other"
}
```

### 型スイッチ

インターフェース変数の動的型を判定する:

```go
switch v := val.(type) {
case string:
    fmt.Println("string:", v)
case int:
    fmt.Println("int:", v)
default:
    fmt.Printf("unexpected: %T\n", v)
}
```

### ループから抜けるためのラベル

switch内の `break` はswitchのみを終了する。外側のループから抜けるにはラベルを使う:

```go
Loop:
    for _, item := range items {
        switch {
        case item.skip:
            continue Loop
        case item.done:
            break Loop
        }
        process(item)
    }
```

### ラベルなしのbreak

switch内のラベルなし `break` は囲んでいる `for` ループを終了しない。冗長な `break` を追加しない — Goのcaseはデフォルトでフォールスルーしない。

---

## エラーフローのインデント

正常パスを最小インデントに保つ。エラーを先に処理する:

```go
// 良い例 — エラーを先に処理、正常コードは基本インデント
if err != nil {
    // エラー処理
    return err
}
// 正常コードが続く

// 悪い例 — 正常コードがインデントされている
if err != nil {
    // エラー処理
} else {
    // 正常コード
}
```

### 必要な場合はifから初期化を外に出す

```go
// ifの結果がif後も必要な場合:
x, err := f()
if err != nil {
    return err
}
// x を使用

// 以下はダメ:
if x, err := f(); err != nil {
    return err
} else {
    // x を使用（紛らわしい）
}
```
