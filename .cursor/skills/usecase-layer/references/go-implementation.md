# Go でのユースケース層実装

## いつ使うか

- Go で `internal/usecase` の形を決めたいとき
- Input/Output DTO、port interface、`Run()` の形を整理したいとき
- ユースケースのテストしやすい書き方を決めたいとき

## 基本方針

- ユースケースは 1 つの業務目的を表す
- 依存は interface 経由で受ける
- domain object の生成と呼び分けを行うが、ルールの本体は持ち込み過ぎない
- Output は presentation 都合に寄りすぎない DTO に閉じる

## 最小テンプレート

```go
package product

import "context"

type ProductRepository interface {
	Save(ctx context.Context, product *domain.Product) error
}

type Tx interface {
	Do(ctx context.Context, fn func(ctx context.Context) error) error
}

type CreateInput struct {
	OwnerID     string
	Name        string
	Description string
	Price       int64
}

type CreateOutput struct {
	ID string
}

type CreateUseCase struct {
	tx   Tx
	repo ProductRepository
}

func NewCreateUseCase(tx Tx, repo ProductRepository) *CreateUseCase {
	return &CreateUseCase{tx: tx, repo: repo}
}

func (uc *CreateUseCase) Run(ctx context.Context, input CreateInput) (*CreateOutput, error) {
	var out *CreateOutput

	err := uc.tx.Do(ctx, func(ctx context.Context) error {
		product, err := domain.NewProduct(input.OwnerID, input.Name, input.Description, input.Price)
		if err != nil {
			return err
		}
		if err := uc.repo.Save(ctx, product); err != nil {
			return err
		}
		out = &CreateOutput{ID: product.ID().String()}
		return nil
	})
	if err != nil {
		return nil, err
	}

	return out, nil
}
```

## Point

- `Run()` は入口として分かりやすく保つ
- transaction を interface にしてテストしやすくする
- DTO と domain object を役割で分ける
- `context.Context` はユースケース境界から下へ渡す

## Port の扱い

- repository や外部 API client への依存は interface で受ける
- その interface をどこに置くかは、誰の関心かで決める
- 集約の境界を表す repository interface は domain 側
- メール送信、決済 API、ジョブ投入のようなユースケース固有の外部依存は usecase 側 port でもよい
- 集約 repository と外部依存 port を同じ粒度で扱わない

## エラー

- domain 由来のエラーは domain で定義されたものを尊重する
- usecase 固有の失敗は application error として包んでよい
- presentation 向けの HTTP status 変換は usecase でやらない

## テスト方針

- domain object はモックしない
- repository、tx、external client をスタブ化する
- 正常系だけでなく、途中失敗時のロールバックや副作用未実行も確認する
