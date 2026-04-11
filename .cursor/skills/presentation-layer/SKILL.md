---
name: presentation-layer
description: Defines presentation-layer guidance for this repository in DDD x Clean Architecture, including controller and presenter responsibilities, request and response conversion, formatting, API and UI-facing validation, error mapping, authentication/session bridging, framework dependency isolation, and `internal/presentation` or interface-adapter splitting. Expected outputs include concise presentation-layer recommendations with reasons, placement guidance, request/response mapping notes, or small Go-oriented handler templates with assumptions. Use when designing, implementing, reviewing, or documenting the presentation layer in this repository.
---

# プレゼンテーション層

## いつ使うか

- プレゼンテーション層に何を置き、何を置かないか判断したいとき
- controller、handler、presenter、view model の責務を切り分けたいとき
- request/response の変換をどこで行うか整理したいとき
- 書式変換、表示用変換、HTTP status 変換をどこに置くか決めたいとき
- API 向けバリデーションと domain ルールの境界を整理したいとき
- 認証情報、セッション情報、共通例外ハンドラーをどこへ置くか決めたいとき
- `internal/presentation` や interface adapter 層の構成を決めたいとき

## このスキルの対象

- このリポジトリの **DDD x クリーンアーキテクチャにおけるプレゼンテーション層**
- Web API、HTML、cron など、ユースケースの呼び出し元としての入出力実装
- request spec、response spec、表示用変換、共通エラーハンドリング

このスキルは、単一集約の不変条件やユースケース本体を定義しない。  
その判断が必要なら `../domain-layer/SKILL.md` と `../usecase-layer/SKILL.md` を併読する。

## 期待する出力

- プレゼンテーション層の判断では、**結論、理由、置き場所、注意点** を短く分けて返す
- 実装相談では、**何を presentation に閉じ込めるか** を最初に明示する
- request/response が絡む場合は、**request mapping、usecase 呼び出し、response mapping、error mapping** を分けて返す

## 基本原則

- **プレゼンテーション層はクライアントとアプリケーションの入出力を実現する**
- **request/response の変換は presentation に閉じ込める**
- **表示用書式変換は presentation の責務**
- **Web フレームワーク依存は presentation に閉じ込める**
- **domain object をそのまま UI/API 向けに晒しすぎない**
- **ユースケース DTO に表示用メソッドを持たせない**
- **認証方法やセッション実装の詳細は presentation に閉じ込める**
- **API 仕様として公開する入力制約は presentation でも扱ってよい**
- **domain ルールと API 入力制約を混同しない**
- **コントローラーから呼ぶ usecase はまず 1 つに保つ**
- **値オブジェクト生成は原則 usecase、ただし ID 変換のような明確な例外はルール化した上で presentation 許容もあり得る**
- **query service を使う場合でも、表示変換の最後の責務は presentation に残す**
- **fat controller を作らず、調停の本体は usecase に寄せる**

## 最初に確認する

1. これは request/response の変換か、domain ルールの本体か
2. 表示や書式の問題か、業務ルールの問題か
3. Web フレームワークや認証ライブラリの知識をどこへ閉じ込めるべきか
4. domain object をそのまま返してよいか、view model / response へ変換すべきか
5. API 仕様として外部へ公開するバリデーションか、domain の不変条件か

判断、実装、レビューでは、**該当する論点の `references/*.md` を開いてから** 進める。

## 作業の入口

### 1. プレゼンテーション層の責務を判断したい

- `references/presentation-core.md` を読む
- request/response、controller、presenter、書式変換、認証の境界を扱う

### 2. Go の実装パターンまで欲しい

- `references/go-implementation.md` を読む
- `handler.go` `request.go` `response.go` の切り方、DTO 詰め替え、error response を扱う

### 3. `internal/presentation` の構成を決めたい

- `references/directory-splitting.md` を読む
- handler/request/response/settings の分割、エンドポイント単位の構成を扱う

### 4. バリデーションや例外ハンドリングを整理したい

- `references/validation-and-errors.md` を読む
- API 入力制約、domain との重複、共通 exception handler、status mapping を扱う

### 5. query service や認証 bridge も含めて責務を見たい

- `references/presentation-core.md` を読む
- query service との接続、session bridge、controller/presenter の分離可否も扱う

## 判断順序

1. まず問いが **表示・入出力の責務** か **domain/usecase の責務** かを切り分ける
2. presentation に置くと決めたら、request mapping、認証、usecase 呼び出し、response mapping の順で責務を確認する
3. API バリデーションがあるなら、domain ルールとの重複を許容するか判断する
4. controller から複数 usecase を呼びたくなったら、まず独立クラスへの切り出しや責務の見直しを検討する
5. domain object を返す場合は、表示処理が逆流しないガードがあるか確認する
6. フレームワーク依存やライブラリ依存は、presentation に留められているか確認する

## してはいけないこと

- request struct や framework context を usecase へそのまま渡すこと
- domain object に表示用メソッドを生やすこと
- Output DTO に表示用書式変換を持たせること
- controller で複数集約の業務ルールを実装すること
- 認証ライブラリの型を usecase や domain に漏らすこと
- HTTP status や JSON 形式の都合を domain/usecase に持ち込むこと
- 共通処理の名目で fat controller や巨大 middleware を作ること

## 追加資料

- プレゼンテーション層の責務、controller、presenter、書式変換: [references/presentation-core.md](references/presentation-core.md)
- Go での handler/request/response、DTO 詰め替え: [references/go-implementation.md](references/go-implementation.md)
- `internal/presentation` の分割と構成: [references/directory-splitting.md](references/directory-splitting.md)
- バリデーション、例外、共通エラーハンドリング: [references/validation-and-errors.md](references/validation-and-errors.md)
- 具体例: [examples.md](examples.md)
