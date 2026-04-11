# Go でのプレゼンテーション層実装

## いつ使うか

- Go で `internal/presentation` の handler をどう書くか決めたいとき
- `request.go` `response.go` `handler.go` の分け方を整理したいとき
- framework context と usecase DTO の境界を決めたいとき

## 基本方針

- framework 依存は handler に閉じ込める
- request struct は presentation に置く
- request struct をそのまま usecase に渡さず、Input DTO に詰め替える
- usecase の結果は response/view model に変換して返す

## 最小テンプレート

```go
package products

import (
	"context"
	"net/http"

	"github.com/gin-gonic/gin"
	productuc "example/internal/usecase/product"
)

type Handler struct {
	create *productuc.CreateUseCase
}

type PostProductsRequest struct {
	OwnerID     string `json:"owner_id" binding:"required"`
	Name        string `json:"name" binding:"required"`
	Description string `json:"description"`
	Price       int64  `json:"price" binding:"required"`
}

type ProductResponse struct {
	ID    string `json:"id"`
	Name  string `json:"name"`
	Price string `json:"price"`
}

func (h *Handler) PostProducts(ctx *gin.Context) {
	var req PostProductsRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, ErrorResponseFromBind(err))
		return
	}

	usecaseCtx := context.Background()
	if ctx.Request != nil {
		usecaseCtx = ctx.Request.Context()
	}

	out, err := h.create.Run(usecaseCtx, productuc.CreateInput{
		OwnerID:     req.OwnerID,
		Name:        req.Name,
		Description: req.Description,
		Price:       req.Price,
	})
	if err != nil {
		WriteUseCaseError(ctx, err)
		return
	}

	ctx.JSON(http.StatusCreated, ProductResponse{
		ID:    out.ID,
		Name:  out.Name,
		Price: FormatPrice(out.Price),
	})
}
```

## Point

- `ctx.ShouldBindJSON()` のような framework API は presentation に留める
- `binding` や request tag は presentation に置く
- usecase へは `*gin.Context` ではなく `context.Context` を渡す
- 書式変換は `FormatPrice()` のように response 側で行う
- usecase DTO に表示用メソッドを持たせない

## よくある分割

```text
internal/presentation/products/
├─ handler.go
├─ request.go
└─ response.go
```

必要なら:

```text
internal/presentation/shared/
├─ error_response.go
└─ auth/
```

## 避けたいこと

- `*gin.Context` のような framework 固有の context を usecase に渡す
- request struct を usecase Input DTO と兼用する
- response 生成の中で domain object の display 用メソッドに頼る
