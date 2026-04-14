# Architecture

この文書は、このリポジトリの変わりにくい構造を説明する。
目的は、実装の量に関わらず「どこに何を置くか」「どの境界を崩さないか」を
判断できる状態を保つことにある。

ここでは個別 API の詳細や一時的な実装都合は扱わない。
代わりに、責務分担、依存方向、文書の位置づけ、不変条件を記述する。

## 全体像

このリポジトリは、Go・Gin・slog を前提にした
DDD x クリーンアーキテクチャのバックエンドテンプレートである。

現時点では実装よりも骨組みが先に用意されているため、
この文書は機能一覧ではなく配置と分割の基準として読む。

高レベルな関係は次のとおり。

```text
External Client / External System
                |
                v
     internal/presentation
                |
                v
         internal/usecase
                |
                v
          internal/domain
                ^
                |
          internal/infra

internal/infra は内側の層が定義した抽象を実装する
cmd/api + internal/config は各層を組み立てる
docs/domain: 業務の言葉とユースケース
docs/api: HTTP 契約
```

コードの中心は `internal` にあり、`cmd/api` が組み立ての入口になる。
`docs/domain` と `docs/api` は補助資料ではなく、
それぞれ業務理解と外部契約の正しい入口として扱う。

## Code Map

- `cmd/api`: アプリケーションの起動点。依存関係の組み立てと起動だけを担う。
- `internal/config`: 環境変数や設定値の読み込み・解釈を担う。
- `internal/domain`: 業務ルールの中核を置く。集約、エンティティ、値オブジェクト、ドメインサービス、リポジトリ抽象などの責務を持つ。
- `internal/usecase`: ユースケース単位の調停を置く。トランザクション境界、副作用順序、複数要素の連携を扱う。
- `internal/presentation`: 外部入出力との橋渡しを置く。HTTP ハンドラ、入出力 DTO、エラー変換、認証文脈との接続などを担う。
- `internal/infra`: DB や外部サービスなどの実装詳細を置く。内側の層が要求する抽象の実装はここに置く。
- `pkg`: `internal` に依存しない再利用可能な要素だけを置く。
- `docs/domain`: 業務用語、ユースケース、モデル理解を支える文書を置く。
- `docs/api`: OpenAPI を含む外部向け HTTP 契約を置く。
- `docker`: コンテナ実行やイメージ化に関する補助ファイルを置く。
- `README.md`: 利用者向けの入口を置く。
- `CONTRIBUTING.md`: 開発参加時の基本ルールを置く。

## どこを見るか

- 業務用語や意味のずれを確認したいときは `docs/domain` を見る。
- ユースケースの流れや調停単位を確認したいときは `docs/domain/usecase` と `internal/usecase` を見る。
- 業務ルールの置き場を確認したいときは `internal/domain` を見る。
- HTTP の入口やレスポンス表現を確認したいときは `internal/presentation` と `docs/api` を見る。
- 永続化や外部サービス接続を確認したいときは `internal/infra` を見る。
- 起動方法や依存の組み立てを確認したいときは `cmd/api` と `internal/config` を見る。
- 利用方法や開発時の前提を確認したいときは `README.md` と `CONTRIBUTING.md` を見る。

## アーキテクチャ上の不変条件

- 依存方向は外側から内側へ向く。`presentation` と `infra` は `usecase` や `domain` を利用してよいが、`domain` は外側の都合を知らない。
- `internal/domain` には業務判断を置き、HTTP、Gin、JSON、SQL、ORM、SDK、設定取得の都合を持ち込まない。
- `internal/usecase` は調停役であり、中核の業務ルールそのものを抱え込まない。業務判断はまず `internal/domain` に置く。
- `internal/presentation` は外部との橋渡しを担い、業務ルール本体や永続化の詳細を持たない。
- `internal/infra` は技術的な実装詳細を閉じ込め、DB モデルや外部 SDK の型を内側へ漏らさない。
- `cmd/api` は composition root であり、業務ロジックの置き場ではない。
- `docs/domain` は業務の意味と意図、`docs/api` は外部契約を表す。両者を混同しない。
- `pkg` には再利用可能なものだけを置き、アプリケーション固有の中心ロジックは `internal` に残す。
- `shared`、`common`、`util` のような曖昧な退避先を増やさず、責務名で分割する。

## 境界

- `internal/domain`: 業務ルールの境界。HTTP 入出力形式、永続化方式、フレームワーク依存を持ち込まない。
- `internal/usecase`: アプリケーションサービスの境界。調停と処理順序を担い、SQL やレスポンス整形は持たない。
- `internal/presentation`: 外部入出力の境界。表現変換を担い、業務ルール本体や永続化実装は持たない。
- `internal/infra`: 技術実装の境界。外部技術との接続を担い、集約の不変条件や API 契約は持たない。
- `docs/domain` と `docs/api`: 文書の境界。前者は業務理解、後者は HTTP 契約を表し、意味や挙動が変わる変更では対応する文書も更新する。

## 横断的な関心事

このリポジトリでは、高凝集・低結合を設計の基本方針とする。
各モジュールは責務を絞り、モジュール間は必要最小限のインターフェースで接続する。

設定は `internal/config` で解釈し、必要な形で各層へ明示的に渡す。
横断的な関心事も、判断と変換の責務が一つの層に混ざらないようレイヤー境界に沿って分ける。

また、コードだけでなく文書も成果物として扱う。
利用方法、用語、契約、挙動に影響する変更では、
`README.md`、`docs/domain`、`docs/api` など関連文書の更新を伴うことを前提にする。

## この文書の見方

この文書は、現在の実装を列挙するためのものではない。
新しいコードや文書をどこへ置くべきか、
どの境界を保つべきかを判断するための基準として使う。
