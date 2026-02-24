# テスト

出典: [Go Test Comments](https://go.dev/wiki/TestComments), [Code Review Comments](https://go.dev/wiki/CodeReviewComments), [Google Style Guide](https://google.github.io/styleguide/go/decisions), [Google Best Practices](https://google.github.io/styleguide/go/best-practices)

## 目次
- [テーブル駆動テスト](#テーブル駆動テスト)
- [テスト失敗メッセージ](#テスト失敗メッセージ)
- [アサートライブラリを使わない](#アサートライブラリを使わない)
- [cmpパッケージ](#cmpパッケージ)
- [t.Error vs t.Fatal](#terror-vs-tfatal)
- [テストヘルパー](#テストヘルパー)
- [サブテスト](#サブテスト)
- [エラーのセマンティクスをテストする](#エラーのセマンティクスをテストする)
- [テストダブル](#テストダブル)
- [ゴルーチンとt.Fatal](#ゴルーチンとtfatal)

---

## テーブル駆動テスト

### いつ使うか
- 多くの異なるケースで類似したテストロジックがある場合
- 関数の出力が期待値と等しいことをテストする場合

### いつ使わないか
- テストケースごとに異なるロジックが必要な場合
- テーブルの各エントリに条件分岐が必要な場合
- 異なるロジックだが同一のセットアップ: 単一関数内のサブテストシーケンスを使う

### 組み合わせ
通常出力のテストとエラー出力のテストで別々のテーブル駆動テスト関数を書く。

### 構造体リテラルのフィールド名

大きなテストケース（20-30行以上）、隣接する同一型フィールド、ゼロ値を省略するフィールドがある場合はフィールド名を指定する:

```go
tests := []struct {
    name    string
    input   string
    want    string
    wantErr bool
}{
    {
        name:  "empty input",
        input: "",
        want:  "",
    },
    {
        name:    "invalid input",
        input:   "bad",
        wantErr: true,
    },
}
```

---

## テスト失敗メッセージ

### 関数を特定する

テスト関数名から自明であっても、失敗メッセージに関数名を含める:

```go
// 良い例
t.Errorf("YourFunc(%q) = %d; want %d", tt.in, got, tt.want)

// 悪い例
t.Errorf("got %v, want %v", got, want)
```

### 入力を特定する

入力が短い場合は含める。大きいまたは不透明な入力の場合はテストケース名で説明する。テーブルインデックスはテストの特定に使わない。

### got（実際値）を先に、want（期待値）を後に

```go
if got != tt.want {
    t.Errorf("Foo(%q) = %d; want %d", tt.in, got, tt.want)
}
```

### 差分を出力する

大きな出力の場合は両方の値を出力する代わりに差分を表示する:

```go
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("Foo() mismatch (-want +got):\n%s", diff)
}
```

---

## アサートライブラリを使わない

アサートライブラリは避ける。

### 問題
- テストを早期に停止するか、興味深い情報を省略する
- Go自体の代わりにサブ言語の作成を強制する
- 不正確なテストを書きやすくする
- 言語に既にある機能を重複する

```go
// 悪い例
assert.IsNotNil(t, "obj", obj)
assert.StringEq(t, "obj.Type", obj.Type, "blogPost")

// 良い例
if obj == nil || obj.Type != "blogPost" || obj.Comments != 2 || obj.Body == "" {
    t.Errorf("AddPost() = %+v", obj)
}
```

Go自体を使ってテストを書く。ミニ言語を作成しない。

---

## cmpパッケージ

複雑な構造体の比較には [`cmp`](https://pkg.go.dev/github.com/google/go-cmp/cmp) パッケージを使う:

```go
import "github.com/google/go-cmp/cmp"

// 等値比較
if !cmp.Equal(got, want) {
    t.Errorf("Foo() = %v, want %v", got, want)
}

// 人間が読みやすい差分
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("Foo() mismatch (-want +got):\n%s", diff)
}
```

### cmpを使う理由
- Goチームが保守
- Goバージョン更新間で安定した結果
- ユーザー設定可能
- ほとんどの比較ニーズに対応

### reflect.DeepEqual について
- 古いコードで使用される
- 非公開フィールドや実装詳細に敏感
- 新しいコードでは `cmp` を優先

### 完全な構造体を比較する

フィールドごとの比較ではなく、構造体全体を一括で比較する:

```go
// 良い例
want := &Config{Timeout: 30, MaxRetries: 3}
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("mismatch (-want +got):\n%s", diff)
}

// 悪い例
if got.Timeout != 30 {
    t.Errorf("Timeout = %d, want 30", got.Timeout)
}
if got.MaxRetries != 3 {
    t.Errorf("MaxRetries = %d, want 3", got.MaxRetries)
}
```

### 安定した結果を比較する

外部パッケージの出力安定性に依存する結果を比較しない。文字列の厳密一致ではなくセマンティックな等価性をテストする。

---

## t.Error vs t.Fatal

### t.Error — テストを続行
- 個別のテストケースの失敗に使用
- `continue` と合わせて使用（`t.Run` なしのテーブルテスト）

### t.Fatal — テストを即座に停止
- セットアップ失敗でテストが続行不可能な場合
- `t.Run` サブテスト内で使用（現在のサブテストのみ終了）

```go
// テーブル駆動テストでt.Runを使う場合
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        got := Foo(tt.input)
        if got != tt.want {
            t.Fatalf("Foo(%q) = %q; want %q", tt.input, got, tt.want)
        }
    })
}
```

### 原則: テストを続行する
テストは失敗後も続行して、1回の実行で全ての失敗チェックを出力すべき。「もぐらたたき」を防ぐ。

---

## テストヘルパー

セットアップ/ティアダウンを行う関数（テスト対象コードに依存しない）。

### t.Helper() を呼ぶ

`*testing.T` を受け取る場合、`t.Helper()` を呼んでヘルパーが呼ばれた行に失敗を帰属させる:

```go
func TestSomeFunction(t *testing.T) {
    golden := readFile(t, "testdata/golden.txt")
    // ...
}

func readFile(t *testing.T, filename string) string {
    t.Helper()
    contents, err := os.ReadFile(filename)
    if err != nil {
        t.Fatal(err)
    }
    return string(contents)
}
```

### 注意
- テスト失敗とその原因の接続を曖昧にする場合は `t.Helper()` を使わない
- アサートライブラリの実装には使わない
- `t.Cleanup()` (Go 1.14+) をリソースのクリーンアップに使用

---

## サブテスト

`t.Run` を使ってテーブルのエントリごとにサブテストを作成:

```go
func TestFoo(t *testing.T) {
    tests := []struct {
        name  string
        input string
        want  string
    }{
        {name: "empty", input: "", want: ""},
        {name: "hello", input: "hello", want: "HELLO"},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Foo(tt.input)
            if got != tt.want {
                t.Errorf("Foo(%q) = %q; want %q", tt.input, got, tt.want)
            }
        })
    }
}
```

### 人間が読めるサブテスト名
- テスト結果がエスケープ後も読みやすいことを確認（テストランナーはスペースをアンダースコアに置換）
- サブテスト本体内で `t.Log` を使うか、失敗メッセージに入力を含める

---

## エラーのセマンティクスをテストする

### 文字列比較を使わない

エラー文字列の比較は脆弱 — メッセージの書き換えで壊れる:

```go
// 悪い例
if err.Error() != "file not found" {
    t.Errorf("unexpected error: %v", err)
}

// 良い例 — 構造的に検査
if !errors.Is(err, os.ErrNotExist) {
    t.Errorf("unexpected error: %v", err)
}
```

### 正確なエラー型が重要でないAPI
- `fmt.Errorf` でエラーメッセージを作成
- ユニットテストではエラーがnilか非nilかのみテスト

### エラー文字列のプロパティテスト
- 例外として、エラーメッセージにパラメータ名が含まれるかのチェックは許容

---

## テストダブル

### 命名
- テストパッケージ名には「test」を付加: `creditcardtest`
- 複数のテストダブルが必要な場合は振る舞いに基づく名前: `AlwaysCharges`, `AlwaysDeclines`
- ローカルテスト変数にはテストダブルの種類をプレフィックス: `spyCC`

### 実トランスポートの使用
テストコードとテストダブルの接続には実際の基盤トランスポート（HTTP、RPC）を使用する。テスト専用サーバーとプロダクションクライアントの組み合わせを優先。

---

## ゴルーチンとt.Fatal

テスト関数以外のゴルーチンから `t.FailNow`、`t.Fatal` などを呼ばない。代わりに `t.Error` を使ってreturnする:

```go
// 悪い例
go func() {
    // ...
    t.Fatal("failed")  // 別のゴルーチンから — 危険
}()

// 良い例
go func() {
    // ...
    t.Error("failed")  // t.Errorは安全
}()
```
