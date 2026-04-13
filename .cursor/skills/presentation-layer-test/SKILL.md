---
name: presentation-layer-test
description: This skill should be used for `internal/presentation`, handlers, controllers, presenters, request/response mapping, error mapping, authentication bridge, middleware, presentation tests, プレゼンテーション層テスト, and テスト項目表 in this repository. It organizes presentation test viewpoints, creates a unit/handler-integration-aware test case matrix from user requirements and relevant code or docs, revises the matrix based on feedback, and generates Go test code only after explicit approval.
---

# プレゼンテーション層テスト

## いつ使うか

- `internal/presentation` のテストを新規作成したいとき
- handler、controller、presenter、view model のテスト観点を整理したいとき
- 先に「プレゼンテーション層テストで何を見るべきか」を決めてから項目表へ落としたいとき
- `unit` と `handler integration` の境界を明示してからテスト設計したいとき
- 項目表をユーザーと合意してから Go のテストコードへ落としたいとき

## このスキルの対象

- このリポジトリの **DDD x クリーンアーキテクチャにおけるプレゼンテーション層テスト**
- `internal/presentation` 配下に置く Go のテスト
- handler / controller
- presenter / response mapper
- request struct / response struct
- 認証 bridge、共通 error handler、middleware
- HTTP 以外の入口としての cron、scheduler、CLI adapter などの presentation 実装

このスキルは、単一集約の不変条件やユースケース本体の調停は主対象にしない。  
それらが主題なら `domain-layer` や `usecase-layer` の判断を優先する。

## 期待する出力

- 第 1 段階では、**観点整理** を返す
- 第 2 段階では、`unit` / `handler integration` を分けた **テスト項目表** を返す
- 第 3 段階では、ユーザー指摘を反映した **修正版の項目表** を返す
- 第 4 段階では、承認済み項目表に沿った **Go のテストコード** を作成する
- 各段階で、**対象、観点、前提、テスト種別、期待結果、境界の判断** を短く明示する

## 基本原則

- **先に観点整理、次に表、最後にコード**
- **プレゼンテーション層テストは domain / usecase の責務と混ぜない**
- **`unit` と `handler integration` の境界を先に明示する**
- **request/response 変換、error mapping、status 変換、認証 bridge を重視する**
- **フレームワーク依存は presentation に閉じ込め、その境界をテストで確認する**
- **API 仕様として公開する入力制約は presentation で確認してよい**
- **外部契約が `docs/api` にあるなら、その契約と presentation の request/response が矛盾しないかを意識する**
- **domain ルール本体の再検証はしない**
- **ユーザーの明示承認があるまで、テストコードは作らない**

## 最初に確認する

1. ユーザーが求めているのは **観点整理** か **項目表** か **コード生成** か
2. 対象は handler、presenter、middleware、共通 error handler、auth bridge のどれか
3. これは `unit` で閉じる話か、`handler integration` が必要か
4. 何を隔離したいのか: framework、認証ライブラリ、request/response 形式、routing
5. request parsing、validation、error mapping、status 変換、認証 bridge のどれが主題か
6. HTTP 入口か、cron / scheduler / CLI のような別入口か
7. 既存実装や既存テストに router 初期化、`httptest`、test helper の流儀があるか

必要情報が不足する場合は、推測で埋め切らず、前提を明示して確認する。

## 作業の入口

### 1. 観点を整理する

- まず `AGENTS.md` と `ARCHITECTURE.md` を確認する
- 必要に応じて `../presentation-layer/SKILL.md` と `../go-implementation/SKILL.md` を確認する
- validation、error、認証 bridge が主題なら、必要に応じて `../presentation-layer/references/validation-and-errors.md` も確認する
- handler / presenter の分割や view model の切り方が主題なら、必要に応じて `../presentation-layer/references/presentation-core.md` や `../presentation-layer/references/directory-splitting.md` も確認する
- ユーザー入力、添付ファイル、`@docs`、対象コードから材料を集める
- 次の観点セットを基準に、必要な観点だけを選ぶ

1. request parsing
2. request validation
3. request mapping
4. 認証 / セッション bridge
5. usecase 呼び出し
6. response mapping
7. 表示用書式変換
8. error mapping
9. HTTP status / response code
10. middleware / routing
11. framework 依存の隔離
12. API 契約整合
13. 回帰

### 2. 項目表を作る

- `unit` と `handler integration` を分けて表へ落とす
- handler、presenter、middleware を同じ観点で無理に埋めない
- 対象に不要な観点は省略してよい
- 省略した観点があれば補足へ短く書く

### 3. 項目表を修正する

- ユーザー指摘を受けたら、行を追加、削除、統合、分割する
- 修正時は「何を変えたか」を短く添える

### 4. テストコードを作る

- 承認済み項目表を source of truth として扱う
- `unit` は usecase stub、formatter stub、auth bridge stub などで閉じる
- `handler integration` は `httptest` や router 初期化を通して確認する
- HTTP 以外の入口では、`handler integration` を「presentation integration」と読み替えてよい
- framework 依存や routing 設定が主題なら、その前提を結果に明記する
- domain や usecase の責務が混ざる場合は、コード化前に先に報告する

### 承認の判定

- 次段階へ進む条件は、**直前に提示した項目表に対する明示承認** があること
- 明示承認の例: `OK`, `いいよ`, `進めて`, `LGTM`, `これでテストコードを書いて`, `表はこれでよい`
- 表を修正したあとは、**修正版に対して改めて承認** を取る
- いきなりコード作成を求められても、直前の項目表が未承認なら、項目表を再提示または要約して確認する
- 承認が曖昧なら、コード化へ進まず 1 文で確認する

## 項目表の作り方

### 推奨カラム

次の列を基本形とする。

| No | テスト種別 | 対象 | 観点 | 事前状態/入力 | 実行 | 期待結果 | 備考 |
|---|---|---|---|---|---|---|---|
| 1 | `unit` |  |  |  |  |  |  |

### 観点の使い分け

- handler / controller:
  - `request parsing`
  - `request validation`
  - `request mapping`
  - `認証 / セッション bridge`
  - `usecase 呼び出し`
  - `response mapping`
  - `error mapping`
  - `HTTP status / response code`
  - `middleware / routing`
  - `framework 依存の隔離`
  - `API 契約整合`
  - `回帰`
- presenter / response mapper:
  - `response mapping`
  - `表示用書式変換`
  - `error mapping`
  - `API 契約整合`
  - `回帰`
- middleware / auth bridge:
  - `認証 / セッション bridge`
  - `middleware / routing`
  - `HTTP status / response code`
  - `framework 依存の隔離`
  - `回帰`

### 表の出し方

- 先に 1 行で対象と前提を書く
- その下に Markdown 表を置く
- 表の行は、基本として **`unit` を先、`handler integration` を後** にする
- 同じテスト種別の中では、**観点の分類順を優先** して並べる
- HTTP 以外の入口では、表の `handler integration` を `presentation integration` と読み替えてよい
- 表の下に、今回使った観点の意味を 1 行ずつ短く補足してよい
- 観点が強く重なる行は、無理に分けず統合してよい
- 表の後に、**domain / usecase / presentation の境界で除外した項目** があれば短く書く

### 観点の短い説明

- `request parsing`: JSON、path、query、form を正しく読み取れること
- `request validation`: API 仕様として公開する入力制約を正しく弾けること
- `request mapping`: request struct から usecase Input DTO へ正しく詰め替えること
- `認証 / セッション bridge`: framework や認証ライブラリの情報を内側向け抽象へ正しく変換すること
- `usecase 呼び出し`: 正しい usecase を、正しい入力で呼ぶこと
- `response mapping`: usecase 出力を API / UI 向け response へ正しく変換すること
- `表示用書式変換`: 日付、価格、ラベルなどの見せ方を presentation で正しく整えること
- `error mapping`: bind error、domain error、usecase error、unexpected error を client 向け表現へ変換すること
- `HTTP status / response code`: 200、201、400、401、403、404、409、500 などを正しく返すこと
- `middleware / routing`: middleware 適用や routing 設定が endpoint に正しく効くこと
- `framework 依存の隔離`: framework 固有型や API が usecase 側へ漏れていないこと
- `API 契約整合`: `docs/api` や公開レスポンス仕様と request/response 形式が矛盾しないこと
- `回帰`: 過去の bind、status、response format、auth 周りの不具合が再発しないこと

## コード生成のルール

- 先に表との対応関係を確認する
- `unit` と `handler integration` を同じファイルへ雑に混ぜない
- framework 固有 assertion は presentation 側へ閉じる
- domain ルール本体や usecase の調停を presentation test で再検証しすぎない
- router や middleware 初期化が必要な場合は、その前提を結果に明記する

## してはいけないこと

- いきなりテストコードを書き始めること
- `unit` と `handler integration` の境界を曖昧なまま項目表を作ること
- request validation があるから domain validation は不要だと扱うこと
- `*gin.Context` のような framework 型を usecase へ渡す前提でテストを書くこと
- HTTP status や JSON 形式の都合を domain / usecase の責務として扱うこと
- user approval 前に「表は仮でいいから」とコード化へ進むこと

## 回答テンプレート

### 観点整理を返すとき

1. **対象**: 何のプレゼンテーション層テストか
2. **前提**: どの情報を根拠にしたか
3. **観点整理**: 今回採用する観点一覧
4. **補足**: `unit` / `handler integration` の切り分け、除外した責務

### 項目表を返すとき

1. **対象**: 何のテスト項目表か
2. **前提**: どの情報を根拠にしたか
3. **項目表**: Markdown 表
4. **観点の説明**: 今回使った観点の意味を短く補足
5. **補足**: 除外した責務、未確定事項、確認したい点

### 修正版を返すとき

1. **変更点**: 何を追加、削除、修正したか
2. **修正版の項目表**
3. **観点の説明**: 必要なら更新後の観点を短く補足
4. **確認事項**: 必要なら 1 つか 2 つ

### コード生成に進むとき

1. 承認済み項目表との対応を短く示す
2. `unit` と `handler integration` をどのファイルへ作るか示す
3. 実装後に、表の各観点をどこまでカバーしたかを短く報告する

## 追加資料

- プレゼンテーション層の責務とテスト境界: [../presentation-layer/SKILL.md](../presentation-layer/SKILL.md)
- Go での handler / request / response 実装: [../go-implementation/SKILL.md](../go-implementation/SKILL.md)
- 例: [examples.md](examples.md)
