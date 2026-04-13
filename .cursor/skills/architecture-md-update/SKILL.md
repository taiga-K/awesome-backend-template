---
name: architecture-md-update
description: Update `ARCHITECTURE.md` for this repository by documenting the project's high-level architecture, code map, invariants, and boundaries without overfitting to volatile implementation details. Use when the user asks to create, update, refine, or review `ARCHITECTURE.md`.
---

# Architecture MD Update

このスキルは、このリポジトリの `ARCHITECTURE.md` を更新するときに使う。

目的は、実装の細部ではなく、変わりにくい構造を短く正確に記述すること。

## まず確認する

1. `AGENTS.md`
2. 既存の `ARCHITECTURE.md`
3. `README.md`
4. `CONTRIBUTING.md`
5. `docs/domain`
6. `docs/api`
7. `internal` と `cmd`

必要に応じて `.cursor/rules` や `.cursor/skills` も参照してよい。

## この文書で書くこと

- プロジェクトの全体像
- コードマップ
- レイヤーやシステムの境界
- 不変条件
- どこを見れば何が分かるか

## この文書で書かないこと

- 変わりやすい関数名や一時的な実装都合
- 個別 API の詳細一覧
- 将来の予定を断定した説明
- ツール固有の運用詳細の列挙

## 書き方の原則

- 高レベルから低レベルへ書く
- ファイルやモジュールはリンクせず、名称で検索できる前提で書く
- 「何があるか」だけでなく「何を置かないか」も書く
- 読み手が「どこを見ればよいか」を判断できるようにする
- コードから読み取りにくい境界や不変条件を優先して明文化する
- 実装が薄い場合は、実装済み機能の一覧ではなく、構造と責務の地図として書く
- 根拠のない業務詳細は補わない

## 推奨構成

必要に応じて見出し名は調整してよいが、次の流れを基本にする。

1. 全体像
2. Code Map
3. どこを見るか
4. アーキテクチャ上の不変条件
5. 境界
6. 横断的な関心事

## このリポジトリ向けの観点

- `internal/domain` は業務ルールの中核
- `internal/usecase` は調停、トランザクション境界、副作用順序
- `internal/presentation` は外部入出力との橋渡し
- `internal/infra` は DB や外部サービスなどの実装詳細
- `internal/config` と `cmd/api` は設定と組み立て
- `docs/domain` は業務の言葉とユースケース
- `docs/api` は HTTP 契約

上記は責務の方向性として扱い、実装や文書に根拠がない細部までは広げない。

## 更新手順

1. 現在の `ARCHITECTURE.md` を読み、残すべき不変の説明と、削るべき変わりやすい説明を分ける
2. リポジトリ構成を見て、実際に存在する主要な置き場を確認する
3. 既存の設計ルールから、依存方向と境界の原則を抽出する
4. 業務詳細が不足している場合は、断定せず、責務分担と文書の置き場に留める
5. `ARCHITECTURE.md` を簡潔に更新する
6. 更新後に読み返し、次を確認する

確認項目:

- 特定の実装に依存しすぎていないか
- 利用開始後に毎回直す必要がある文言が入っていないか
- コードマップが「どこにあるか」「何をするか」「どう関わるか」を満たしているか
- 境界と不変条件が明示されているか

## 迷ったとき

- 詳細を書くか迷ったら削る
- 業務仕様か構造説明か迷ったら、`ARCHITECTURE.md` には構造だけを書く
- 実装がないなら、存在しないモジュールの詳細を作らない
- 変更理由が文書の保守コスト削減なら、その方向を優先する

## 仕上げ

- 変更後に `ARCHITECTURE.md` を読み返して、不自然な断定や重複を消す
- 可能なら最近編集した `ARCHITECTURE.md` の lint を確認する
