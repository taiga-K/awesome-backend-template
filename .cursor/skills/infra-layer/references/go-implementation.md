# Go でのインフラ層実装

## いつ使うか

- Go で repository 実装の形を決めたいとき
- transaction manager や外部 client adapter の置き方を整理したいとき
- `sqlc`, `gorm`, `pgx` などの詳細をどう隔離するか決めたいとき

## 基本方針

- domain interface に合わせて infra 実装を作る
- DB 保存用パラメータへの変換は infra 側で行う
- 取得時は DB row から domain object を再構成する
- generated code や SDK 呼び出しは infra 側で閉じる

## repository の最小テンプレート

```go
package repository

import (
	"context"

	productDomain "example/internal/domain/product"
)

type Queries interface {
	UpsertProduct(ctx context.Context, arg UpsertProductParams) error
	GetProduct(ctx context.Context, id string) (ProductRow, error)
}

type ProductRepository struct {
	query Queries
}

func NewProductRepository(query Queries) productDomain.Repository {
	return &ProductRepository{query: query}
}

func (r *ProductRepository) Save(ctx context.Context, product *productDomain.Product) error {
	return r.query.UpsertProduct(ctx, UpsertProductParams{
		ID:    product.ID().String(),
		Name:  product.Name().Value(),
		Price: product.Price().Value(),
	})
}

func (r *ProductRepository) FindByID(ctx context.Context, id productDomain.ID) (*productDomain.Product, error) {
	row, err := r.query.GetProduct(ctx, id.String())
	if err != nil {
		return nil, err
	}

	name, err := productDomain.NewName(row.Name)
	if err != nil {
		return nil, err
	}
	price := productDomain.ReconstructMoney(row.Price)

	return productDomain.ReconstructProduct(
		productDomain.ID(row.ID),
		name,
		price,
	), nil
}
```

## transaction manager の例

```go
type TxManager interface {
	Do(ctx context.Context, fn func(ctx context.Context) error) error
}
```

- interface は usecase 側にあることが多い
- 実装は infra 側で DB transaction に結びつける

## 外部 client adapter の例

```go
type SlackClient struct {
	httpClient *http.Client
	webhookURL string
}

func (c *SlackClient) Notify(ctx context.Context, n domain.Notification) error {
	// webhook 呼び出し詳細は infra に閉じる
	return nil
}
```

## Point

- `dbgen`, `gorm.Model`, `sqlc` generated type を外へ返さない
- repository の戻り値は domain object に戻す
- domain が意識しない認証、接続設定、retry 設定は infra に置く
- context で request-scoped な DB query や transaction を受け渡す

## テスト方針

- mapping の正しさを table-driven test で確認する
- integration test では本物の DB や test container を使ってもよい
- unit test では query interface や sdk client を差し替える
