# フォーマットとスタイル

出典: [Effective Go](https://go.dev/doc/effective_go#formatting), [Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Google Style Guide](https://google.github.io/styleguide/go/guide)

## 目次
- [gofmt](#gofmt)
- [インポート](#インポート)
- [行の長さ](#行の長さ)
- [セミコロンと波括弧](#セミコロンと波括弧)
- [空スライスの宣言](#空スライスの宣言)
- [複合リテラル](#複合リテラル)
- [変数宣言](#変数宣言)
- [チャネルの方向](#チャネルの方向)
- [インデントと空白](#インデントと空白)

---

## gofmt

全てのコードで `gofmt`（または `go fmt`）を実行する。ほぼ全てのGoコードが使用している。

`goimports` は `gofmt` のスーパーセットとして推奨 — インポート行の追加/削除も自動で行う。

```go
// gofmtは構造体フィールドを揃える:
type T struct {
    name    string // オブジェクトの名前
    value   int    // その値
}
```

### ルール
- インデントにはタブを使う（gofmtのデフォルト）
- スペースは必要な場合のみ使用
- 標準パッケージの全Goコードはgofmtでフォーマット済み
- 生成コードも `format.Source` 経由でgofmtを使用すべき

---

## インポート

### グループ分け

インポートはグループに分け、空行で区切る。標準ライブラリが最初:

```go
package main

import (
    "fmt"
    "hash/adler32"
    "os"

    "github.com/foo/bar"
    "rsc.io/goversion/version"
)
```

`goimports` がこれを自動処理する。

### リネーム

名前の衝突を避ける場合を除き、インポートのリネームは避ける。衝突時は最もローカルまたはプロジェクト固有のインポートをリネームすることを優先する。

```go
// 衝突がある場合は許容される
import (
    fmtpb "path/to/fmt_proto"
    "fmt"
)
```

### ブランク（副作用）インポート

副作用のみのインポートは `import _ "pkg"` を使う。`main` パッケージまたはテストでのみ使用:

```go
import _ "net/http/pprof"
```

### ドットインポート

`import .` は使わない。例外は循環依存によりテスト対象パッケージに属せないテストファイルのみ:

```go
// 許容される唯一のケース:
package foo_test
import (
    . "foo"
    "bar/testutil" // "foo" をインポートしている
)
```

---

## 行の長さ

Goには固定の行長制限はない。意味に基づいて改行する（長さではなく）。

### ガイドライン
- 行が長すぎると感じたら、折り返してタブ1つ追加でインデント
- 短く保つためだけの改行は不要 — 長い方が読みやすい行もある
- インデント変更の前（関数宣言、条件文）では改行しない
- 長い文字列（特にURL）のための改行はしない
- 長い行は長い名前を示唆 — 折り返しではなく名前を短くする

### 禁止される改行
```go
// 悪い例 — 波括弧前の不要な改行
if longCondition1 && longCondition2 &&
    longCondition3 {  // インデントが紛らわしい
    doSomething()
}

// 良い例 — 条件を抽出
needsProcessing := longCondition1 && longCondition2 && longCondition3
if needsProcessing {
    doSomething()
}
```

---

## セミコロンと波括弧

Goはセミコロンを自動挿入する。文を終了し得るトークン（識別子、リテラル、`break`、`continue`、`fallthrough`、`return`、`++`、`--`、`)`、`}`）の後にセミコロンが挿入される。

### 重要ルール: 開き波括弧の配置

制御構造の開き波括弧は必ず同じ行に置く:

```go
// 正しい
if i < f() {
    g()
}

// 間違い — コンパイルエラー（{ の前にセミコロンが挿入される）
if i < f()
{
    g()
}
```

### ソース内のセミコロン

以下にのみ出現する:
- `for` ループ句: `for init; condition; post {}`
- 1行に複数の文（まれ）

---

## 空スライスの宣言

nilスライス宣言を優先する:

```go
// 良い例 — nilスライス
var t []string

// 避ける — nilでないゼロ長スライス
t := []string{}
```

両者は機能的に同等（`len` と `cap` はどちらもゼロ）だが、nilが推奨。

### 例外
JSONエンコード時は `[]string{}` を使う: nilは `null` にエンコードされ、空スライスは `[]` にエンコードされる。

### 設計原則
nilと非nil・ゼロ長スライスを区別するインターフェースは設計しない — 微妙なバグの原因になる。

---

## 複合リテラル

### フィールドラベル

他パッケージの構造体リテラルにはfield:valueペアを使う:

```go
// 良い例 — 明確でフィールド並べ替えに強い
return &File{fd: fd, name: name}

// 内部型で少数フィールドの場合は許容
return &File{fd, name, nil, 0}
```

### ゼロ値フィールドを省略

明確さが必要な場合を除き省略する:

```go
// 良い例
return &Config{
    Timeout:    30 * time.Second,
    MaxRetries: 3,
}

// 不要
return &Config{
    Timeout:    30 * time.Second,
    MaxRetries: 3,
    Debug:      false,  // ゼロ値 — 省略可
    Logger:     nil,    // ゼロ値 — 省略可
}
```

### スライス/マップリテラルでの型名省略

繰り返される型名を省略する:

```go
// 良い例
points := []Point{
    {1, 2},
    {3, 4},
}

// 冗長
points := []Point{
    Point{1, 2},
    Point{3, 4},
}
```

### 空の複合リテラル

`&File{}` は `new(File)` と等価 — どちらもゼロ値を生成。

---

## 変数宣言

### ゼロ値以外には `:=` を使用

```go
// 良い例
i := 42
s := "hello"
p := new(Point)

// あまり慣用的でない
var i int = 42
var s string = "hello"
```

### ゼロ値には `var` を使用

```go
// 良い例 — ゼロ値が有意味
var buf bytes.Buffer
var mu sync.Mutex
var coords Point

// 意図が不明確
buf := bytes.Buffer{}
```

### スライスとマップのサイズヒント

最終サイズが分かっている場合はキャパシティを事前確保:

```go
// 良い例 — サイズが既知
names := make([]string, 0, len(users))
for _, u := range users {
    names = append(names, u.Name)
}
```

ほとんどのコードではこれは不要 — 経験的な証拠に基づいてのみ最適化する。

---

## チャネルの方向

可能な場合は方向を指定する:

```go
// 良い例 — 意図を伝えエラーを防ぐ
func produce(ch chan<- int) {}   // 送信専用
func consume(ch <-chan int) {}   // 受信専用
```

---

## インデントと空白

### 括弧

GoはC/Javaより括弧が少ない:

```go
// Go — 制御構造に括弧不要
if x > 0 {
    return y
}
for i := 0; i < 10; i++ {}
switch val {
case 1:
}
```

### インデントの混乱を避ける

インデントされたブロックと紛らわしい位置で改行しない:

```go
// 悪い例 — 紛らわしい位置揃え
if longVariable := someLongFunction(
    arg1, arg2); longVariable != nil {
    // ...
}

// 良い例
longVariable := someLongFunction(arg1, arg2)
if longVariable != nil {
    // ...
}
```

### 関数のフォーマット

可能な場合はシグネチャを1行に保つ。ローカル変数を抽出して呼び出しを短くする。引数は意味的にグループ化:

```go
// 良い例 — 明確なグループ分け
db.ExecContext(ctx,
    query,
    userID, userName, userEmail,
)
```
