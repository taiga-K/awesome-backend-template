# Go でのドメイン層実装

## いつ使うか

- Go で `internal/domain` の型設計を決めたいとき
- `NewXxx()` と `Reconstruct()` の分離が必要か判断したいとき
- repository interface をどこに置くか整理したいとき
- ORM model と domain model を分離したいとき
- 最小の Go サンプルを添えて説明したいとき

## 基本方針

- ドメインモデルをそのまま Go の型へ寄せる
- 新規生成と永続化済みデータの復元は入口を分けてよい
- フィールドは必要以上に公開せず、状態遷移は業務語彙のメソッドで表す
- repository interface は `domain` に置き、実装は `infra` に置く
- JSON tag、gorm tag、SQL row struct は `domain` に持ち込まない

## まず確認する

1. このルールは単一集約の不変条件か
2. 新規作成時だけ必要な制約か、再構成時にも必要か
3. DB、ORM、HTTP 由来の都合が `domain` に漏れていないか
4. ユースケース層（application層）に残すべき調停を `domain` に押し込んでいないか

## Entity

- 識別子で同一性を持つならエンティティ
- public setter を生やさず、`ChangePrice()` `Complete()` のようなメソッドに寄せる
- 生成時の業務ルールは `NewXxx()` `Create()` に集める
- 再構成は `ReconstructXxx()` のように別経路にしてよい

## Value Object

- 値そのもので同一性を持つなら値オブジェクト
- 可能ならイミュータブルにする
- フォーマット検証、正規化、範囲チェックは生成時に完了させる
- ID、金額、メールアドレス、期間、状態は候補になりやすい

## Repository

- interface は `domain` に置く
- 実装は `infra` に置く
- DB row から domain への詰め替えは repository 実装で隠蔽する
- 集約の一部だけを直接更新する API は避ける

## Domain Service

- エンティティや値オブジェクトへ載せると不自然なルールだけを扱う
- 命名は責務優先で、`XxxService` に固定しない
- repository 利用は許容するが、責務過多に注意する
- 永続化順序やトランザクション制御が中心ならユースケース層を優先する

次のどれかに当てはまるなら、domain service ではなく `internal/usecase` をまず疑う。

- 2 つ以上の repository の呼び順を制御する
- 外部 API や通知送信を直接起動する
- transaction の開始や終了を扱う
- retry、timeout、lock、idempotency を扱う
- DTO を組み立てる

domain service が repository を使う場合も、存在確認、重複確認、集合に対するドメイン判定のような用途に寄せる。

## ユースケース層の境界

- ユースケース層に置く:
  - DTO
  - 認可
  - トランザクション開始
  - 複数集約の調停
  - 外部依存の呼び分け
- `domain` に置く:
  - 単一集約の不変条件
  - 値検証の本体
  - 状態遷移ルール

実装ディレクトリ例:

- `internal/usecase/product/save_product.go`
- `internal/usecase/product/dto.go`

## 最小テンプレート

```go
package product

import "context"

type ProductID string

type Name struct {
	value string
}

func NewName(value string) (Name, error) {
	if value == "" {
		return Name{}, ErrInvalidName
	}
	return Name{value: value}, nil
}

type Product struct {
	id   ProductID
	name Name
}

func NewProduct(id ProductID, name Name) (*Product, error) {
	if id == "" {
		return nil, ErrInvalidID
	}
	return &Product{id: id, name: name}, nil
}

func ReconstructProduct(id ProductID, name Name) *Product {
	return &Product{id: id, name: name}
}

type Repository interface {
	FindByID(ctx context.Context, id ProductID) (*Product, error)
	Save(ctx context.Context, product *Product) error
}
```

## アンチパターン

- `domain` struct に `json` や `gorm` tag を付ける
- ORM model をそのまま domain object として使う
- setter 連打で状態を作る
- `TaskService` のような責務不明なクラス名に逃げる
- repository interface をユースケース層に置いて集約境界を曖昧にする

## 回答時の出し方

1. 結論
2. どの層の責務か
3. Go での置き場所
4. 必要なら最小コード例
5. 避けるべき実装
