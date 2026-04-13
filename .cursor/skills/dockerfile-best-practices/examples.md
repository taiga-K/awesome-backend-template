# Examples

## 例1: Go バックエンドの基本形

`docker/Dockerfile` を新規作成するなら、まずは次のような形を基準にする。
ベースイメージのタグは固定の正解ではなく、`go.mod` の `go` ディレクティブと運用方針に合わせて更新する。

```dockerfile
# syntax=docker/dockerfile:1

FROM golang:<go-version>-alpine AS build

WORKDIR /src

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=${TARGETARCH:-amd64} go build -o /out/api ./cmd/api

FROM alpine:<runtime-version>

RUN apk add --no-cache ca-certificates \
    && addgroup -S app \
    && adduser -S app -G app

WORKDIR /app
COPY --from=build /out/api /app/api

USER app

EXPOSE 8080
ENTRYPOINT ["/app/api"]
```

この例で押さえている点:

- 依存解決に必要な `go.mod` / `go.sum` を先に `COPY` してキャッシュを効かせる
- ビルドステージと実行ステージを分ける
- 最終イメージにコンパイラやソース全体を残さない
- 外向き HTTPS が必要なケースに備えて `ca-certificates` を入れる
- `USER` を設定して root 実行を避ける
- `ENTRYPOINT` を exec 形式で書く
- `TARGETARCH` が渡される環境ではマルチアーキに流用しやすい

## 例2: Debian/Ubuntu 系で `apt-get` を使う場合

Debian/Ubuntu 系のステージ内では、少なくとも次の形を基準にする。

```dockerfile
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*
```

守ること:

- `apt-get update` と `apt-get install` を分けない
- パッケージ一覧は見やすく保つ
- 後始末を同じレイヤで行う

## 例3: 避けたい形

```dockerfile
FROM golang:1.24
COPY . .
RUN go build ./...
CMD go run ./cmd/api
```

問題点:

- `COPY . .` が早すぎてキャッシュ効率が悪い
- 実行時にもビルドツールを抱えたままになる
- 本番起動がビルド依存になり、責務分離が弱い

## 出力時の期待

Dockerfile を提案・生成するときは、コードだけで終えず、必要なら次も一緒に触れる。

- `docker/Dockerfile` をどの前提で置いたか
- `.dockerignore` の追加要否
- ビルドコマンド例
- 残る制約。例: `CGO_ENABLED=0` が使えない、ランタイムに OS パッケージが必要、マルチアーキ対応が必要、など
