# Go 実装・レビューの使い方

このファイルのコードは、方針を伝えるための最小例であり、そのまま貼り付けて使う前提ではない。

## 例1: 新規実装の相談

入力例:

```text
Go で repository を実装したいです。
error の返し方、context の渡し方、interface の切り方も含めて方針をください。
```

期待する進め方:

- まず公開 API と package 境界を確認する
- 次に `context.Context` の入口と伝播先を決める
- interface を利用側都合で最小化する
- `%w` を使った error 方針と、最上位だけでログする方針を出す
- 必要なテスト観点を列挙する

## 例2: PR レビューの依頼

入力例:

```text
この Go の差分をレビューして、バグ、エラー処理、Go らしくない点、足りないテストを指摘してください。
```

期待する進め方:

- 先にバグ、リーク、競合、API 契約違反を探す
- 次に命名、制御フロー、責務分割、不要 interface を確認する
- 最後にテスト不足と doc comment の不足をまとめる
- 指摘は severity 順に返す

## ミニ例: エラーの扱い

Bad:

```go
func Load(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		log.Printf("read file failed: %v", err)
		return err
	}
	_ = data
	return nil
}
```

Good:

```go
func Load(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("read %s: %w", path, err)
	}
	_ = data
	return nil
}
```

理由:

- 下位層で `log + return` をしない
- `%w` で文脈を足して返す
- 最上位で一度だけログやレスポンス変換を行う

## ミニ例: interface の切り方

Bad:

```go
type UserServiceInterface interface {
	CreateUser(ctx context.Context, input CreateUserInput) (*User, error)
	UpdateUser(ctx context.Context, input UpdateUserInput) (*User, error)
	DeleteUser(ctx context.Context, id string) error
}
```

Good:

```go
type UserRepository interface {
	Save(ctx context.Context, user *User) error
	FindByID(ctx context.Context, id string) (*User, error)
}
```

理由:

- 利用側に必要な最小 interface を置く
- 実装を差し替えるためだけの巨大 interface を作らない
- Go では small interface の方が変更に強い
