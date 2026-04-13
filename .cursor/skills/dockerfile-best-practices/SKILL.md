---
name: dockerfile-best-practices
description: Writes and reviews Dockerfiles for this repository using Dockerfile best practices such as multi-stage builds, cache-friendly layer ordering, minimal packages, COPY-over-ADD, non-root execution, and .dockerignore awareness. Use when creating, updating, or reviewing Dockerfiles, container images, build stages, or files under docker/. Also applies to Japanese requests about Dockerfile creation, Dockerfile review, docker/ files, multi-stage builds, and container image optimization.
---

# Dockerfile Best Practices

このスキルは、このリポジトリで `docker/` 配下に Dockerfile を作成・更新・レビューするときに使う。

既定の配置は `docker/Dockerfile` とする。ユーザーが複数イメージや別名を明示したときだけ、`docker/<purpose>.Dockerfile` などに切り替える。

## まず確認する

1. 対象は **新規作成** か **既存 Dockerfile の修正** か
2. 実行対象は **Go アプリ本体** か **補助ツール** か
3. ビルド成果物だけを最終イメージに残せるか
4. ビルドコンテキストに不要ファイルが混ざっていないか
5. root 以外で動かせるか

## 基本方針

- 可能なら **マルチステージビルド** を使い、ビルド用ツールは最終イメージに残さない
- **変更頻度の低いものから先に** 書いて、ビルドキャッシュを活かす
- 不要なパッケージを入れず、コンテナの責務は 1 つに保つ
- ローカルファイルやディレクトリの取り込みは **`COPY` を優先** し、`ADD` は自動展開が必要なときだけ使う
- `WORKDIR` は **絶対パス** を使う
- サービス起動の `CMD` と `ENTRYPOINT` は **exec 形式** を優先する
- 可能なら **非 root ユーザー** で実行する
- `apt-get update` と `apt-get install` は **同じ `RUN`** にまとめ、一覧は見やすく並べ、後始末まで同じレイヤで行う
- パイプを使う `RUN` は、必要なら `pipefail` を考慮して失敗を見逃さない
- Dockerfile だけでなく、必要に応じて `.dockerignore` の追加・更新も提案する

## 作成手順

1. まず `docker/` 配下に置く Dockerfile の用途を 1 文で定義する
2. ベースイメージは、用途に合った **公式イメージ** かつ **できるだけ小さいもの** を選ぶ
3. 依存関係の解決に必要なファイルを先に `COPY` し、依存インストールを先に済ませる
4. アプリ本体のコピーは後ろに置き、差分変更でキャッシュが無駄に壊れないようにする
5. 最終ステージには、実行に必要な成果物だけを `COPY --from=` する
6. 常駐プロセスの起動方法は `CMD ["binary"]` や `ENTRYPOINT ["binary"]` のような exec 形式で書く
7. `VOLUME` は必須ではない。イメージ利用者に既定のマウント先を約束したいときだけ検討し、多くのケースではランタイムやオーケストレーション側で volume を定義する。公開ポートがあるなら `EXPOSE` を明示する
8. 最後に、イメージサイズ、責務分離、キャッシュ効率、運用時の安全性を見直す

## 命令ごとの指針

### `FROM`

- ビルド用と実行用でステージを分ける
- 実行用ステージは、ビルドに不要なツールを含まない最小構成を選ぶ

### `RUN`

- 長いコマンドは複数行に分ける
- Debian/Ubuntu 系では `apt-get update && apt-get install -y ... && rm -rf /var/lib/apt/lists/*` を 1 つの `RUN` にまとめる
- 複数行のパッケージ一覧は、重複を避けるために規則的に並べる

### `COPY` / `ADD`

- 基本は `COPY`
- リモート URL 取得のために `ADD` は使わず、`curl` や `wget` を `RUN` で使う
- 依存定義ファイルとアプリ本体は分けて `COPY` し、キャッシュの粒度を保つ

### `ENV`

- バージョン値や実行時に必要な環境変数だけを定義する
- 一時的な値を永続化したくない場合は `RUN` の中で完結させる

### `USER`

- root 権限が不要なら明示的に非 root ユーザーへ切り替える
- `sudo` は持ち込まない

### `WORKDIR`

- `RUN cd ...` を多用せず、`WORKDIR` で作業ディレクトリを固定する

### アーキテクチャ差分

- サンプルの `GOARCH=amd64` などは固定値ではなく、用途に応じて `arm64` や BuildKit の `TARGETARCH` を検討する
- ベースイメージの具体タグは例示に過ぎないため、`go.mod` や運用方針に合わせて見直す

## レビュー観点

- ビルド用ツールやキャッシュが最終イメージに漏れていないか
- `COPY . .` が早すぎてキャッシュ効率を落としていないか
- `ADD` が不要に使われていないか
- root 実行のままになっていないか
- `CMD` / `ENTRYPOINT` が shell 形式でシグナル伝播を壊していないか
- ビルドコンテキストに不要ファイルを送る構成になっていないか

## 追加資料

- 詳細チェックリスト: [references/checklist.md](references/checklist.md)
- Go バックエンド向け例: [examples.md](examples.md)
