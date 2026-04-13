# Architecture

この文書は、このリポジトリの高レベルな構造と責務分担を説明する。
目的は、「どこに何を置くか」「何をどこに置かないか」を先に共有し、
実装が増えても判断基準がぶれにくい状態を保つことにある。

ここでは、変わりやすい関数名や個別 API の詳細は扱わない。
代わりに、レイヤーの責務、依存方向、文書の位置づけ、不変条件を記述する。

## 全体像

このリポジトリは、Go を前提にした DDD x クリーンアーキテクチャの
バックエンドアプリケーションとして構成する。

現時点の実装は最小限で、主要ディレクトリは「何を置くか」を示す骨組みとして
用意されている。したがって、この文書は実装済み機能の一覧ではなく、
今後の実装をどの責務に沿って配置するかの地図として読む。

高レベルな関係は次のとおり。

```text
Client / External System
        |
        v
      cmd/api
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

docs/domain: 業務の言葉とユースケース
docs/api: 外部 API 契約
```

コードの中心は `internal` にあり、`cmd/api` が起動点になる。
`docs/domain` と `docs/api` はコードの外にある補助資料ではなく、
それぞれ業務理解と外部契約の正しい入口として扱う。

## Code Map

### ルート

- `cmd/api`: アプリケーションの起動点。依存関係の組み立てと起動を担う。
- `internal`: アプリケーション本体。レイヤー別の責務をここに置く。
- `pkg`: `internal` に依存せず再利用できるものだけを置く。
- `docs/domain`: 業務用語、ユースケース、モデル理解の文書を置く。
- `docs/api`: OpenAPI を中心とした外部契約を置く。
- `README.md`: 利用者向けの入口を置く。
- `CONTRIBUTING.md`: 開発参加時の基本ルールを置く。

### `internal`

- `internal/domain`: 業務ルールの中核を置く。集約、エンティティ、値オブジェクト、ドメインサービス、リポジトリ抽象などの責務を担う。
- `internal/usecase`: ユースケース単位の調停を置く。トランザクション境界、副作用の順序、複数要素の連携を扱う。
- `internal/presentation`: 外部入出力との橋渡しを置く。HTTP などの request/response 変換やエラー表現の変換を担う。
- `internal/infra`: DB や外部サービスなどの実装詳細を置く。内側が要求する抽象の実装はここに置く。
- `internal/config`: 設定の読み込みと解釈を置く。

### `docs/domain`

- `ubiquitous-language.md`: 用語の意味と境界を置く。
- `usecase`: ユースケースの流れを置く。
- `uml`: モデル関係の補助表現を置く。

### `docs/api`

`docs/api` は OpenAPI を分割前提で管理する置き場である。
このテンプレートでは、少なくとも `paths` と `components/schemas` を起点にし、
未使用の構成要素を慣習だけで増やさない。

## どこを見るか

- 業務用語を知りたいときは `docs/domain/ubiquitous-language.md` を見る。
- ユースケースの流れを知りたいときは `docs/domain/usecase` を見る。
- 業務ルールの置き場を確認したいときは `internal/domain` を見る。
- 入出力の入口を確認したいときは `internal/presentation` を見る。
- 調停や副作用順序を確認したいときは `internal/usecase` を見る。
- DB や外部サービス接続を確認したいときは `internal/infra` を見る。
- 起動方法や依存の組み立てを確認したいときは `cmd/api` と `internal/config` を見る。
- 外部 API 契約を確認したいときは `docs/api` を見る。

## アーキテクチャ上の不変条件

- 依存方向は外側から内側へ向く。`presentation` と `infra` は `usecase` や `domain` を利用してよいが、`domain` は外側の都合を知らない。
- `internal/domain` には業務判断を置き、HTTP、JSON、ORM、SQL、SDK の都合を持ち込まない。
- `internal/usecase` は調停役であり、単一の業務概念そのものを表現する場所ではない。中核ルールはまず `internal/domain` に置く。
- `internal/presentation` は外部との橋渡しを担い、業務ルール本体や永続化の詳細を抱え込まない。
- `internal/infra` は実装詳細を閉じ込め、DB や外部 SDK の型を内側へ漏らさない。
- `cmd/api` は組み立ての場所であり、業務ロジックの本体を置く場所ではない。
- `docs/domain` は業務の言葉と意図の入口、`docs/api` は外部契約の入口であり、両者を混同しない。
- `pkg` には再利用可能なものだけを置き、アプリケーション固有の中心ロジックは `internal` に残す。
- `shared`、`common`、`util` のような曖昧な退避先を増やさず、責務名で分ける。

## 境界

### Domain Boundary

`internal/domain` には業務ルールを置く。
ここに HTTP 入出力形式、永続化方式、フレームワーク依存を置かない。

### Usecase Boundary

`internal/usecase` には処理順序と調停を置く。
ここに SQL、ORM モデル、レスポンス整形を置かない。

### Presentation Boundary

`internal/presentation` には外部インターフェースを置く。
ここに業務ルールの本体や永続化の詳細を置かない。

### Infrastructure Boundary

`internal/infra` には外部技術との接続を置く。
ここに集約の不変条件や API 契約そのものを置かない。

### Documentation Boundary

`docs/domain` は業務の意味を記述する。
`docs/api` は外部に見せる契約を記述する。
変更によって意味や挙動が変わるなら、対応する文書も整合させる。

## 横断的な関心事

このリポジトリでは、高凝集・低結合を設計の基本方針とする。
各モジュールは責務を絞り、モジュール間は必要最小限のインターフェースで接続する。

また、コードだけでなく文書も成果物として扱う。
利用方法、用語、契約、挙動に影響する変更では、`README.md` や関連文書の更新を伴うことを前提にする。

## この文書の見方

この文書は、「今ある実装」を列挙するものではない。
「新しい実装や文書をどこへ置くべきか」「どの境界を崩さないべきか」を
判断するための基準として使う。
