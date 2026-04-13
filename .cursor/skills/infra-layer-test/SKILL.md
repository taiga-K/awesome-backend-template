---
name: infra-layer-test
description: This skill should be used when designing, refining, reviewing, or implementing infrastructure-layer tests for this repository in DDD x Clean Architecture. It first organizes infra test viewpoints, then creates a unit/integration-aware test case matrix from user requirements and relevant code or docs, revises the matrix based on feedback, and only generates Go test code after explicit approval. Use when the user mentions `internal/infra`, repository implementations, transaction managers, external clients, ORM, SQL, DB row mapping, integration tests, infrastructure tests, インフラ層テスト, or テスト項目表.
---

# インフラ層テスト

## いつ使うか

- `internal/infra` のテストを新規作成したいとき
- repository 実装、transaction manager、外部 client adapter のテスト観点を整理したいとき
- 先に「インフラ層テストで何を見るべきか」を決めてから項目表へ落としたいとき
- `unit` と `integration` の境界を明示してからテスト設計したいとき
- 項目表をユーザーと合意してから Go のテストコードへ落としたいとき

## このスキルの対象

- このリポジトリの **DDD x クリーンアーキテクチャにおけるインフラ層テスト**
- `internal/infra` 配下に置く Go のテスト
- repository 実装
- transaction manager 実装
- 外部 API client / SDK adapter 実装

このスキルは、集約の不変条件やユースケースの処理順序そのものは主対象にしない。  
それらが主題なら `domain-layer` や `usecase-layer` の判断を優先する。

## 期待する出力

- 第 1 段階では、**観点整理** を返す
- 第 2 段階では、`unit` / `integration` を分けた **テスト項目表** を返す
- 第 3 段階では、ユーザー指摘を反映した **修正版の項目表** を返す
- 第 4 段階では、承認済み項目表に沿った **Go のテストコード** を作成する
- 各段階で、**対象、観点、前提、テスト種別、期待結果、境界の判断** を短く明示する

## 基本原則

- **先に観点整理、次に表、最後にコード**
- **インフラ層テストは domain の unit test と混ぜない**
- **`unit` と `integration` の境界を先に明示する**
- **実装詳細の隔離が正しいかを確認し、業務ルール本体の再検証はしない**
- **repository では mapping、再構成、query、transaction、lock を重視する**
- **external client では request 変換、response 変換、error 変換、retry/timeout を重視する**
- **実 DB や実 API 契約に依存する確認は integration として扱う**
- **ユーザーの明示承認があるまで、テストコードは作らない**

## 最初に確認する

1. ユーザーが求めているのは **観点整理** か **項目表** か **コード生成** か
2. 対象は repository、transaction manager、external client、outbox のどれか
3. これは `unit` で閉じる話か、`integration` が必要か
4. 何を隔離したいのか: ORM、SQL、DB、Redis、外部 API、SDK
5. mapping、再構成、transaction、lock、retry のどれが主題か
6. 既存実装や既存テストに命名、ケース粒度、test container 利用の流儀があるか

必要情報が不足する場合は、推測で埋め切らず、前提を明示して確認する。

## 作業の入口

### 1. 観点を整理する

- まず `AGENTS.md` と `ARCHITECTURE.md` を確認する
- 必要に応じて `../infra-layer/SKILL.md` と `../go-implementation/SKILL.md` を確認する
- outbox、楽観ロック、外部 client、ORM の詳細が主題なら、必要に応じて `../infra-layer/references/persistence-and-clients.md` も確認する
- ユーザー入力、添付ファイル、`@docs`、対象コードから材料を集める
- 次の観点セットを基準に、必要な観点だけを選ぶ

1. repository mapping
2. domain 再構成
3. 永続化動作
4. query 条件
5. transaction 実装
6. 排他制御 / version
7. 外部 client request 変換
8. 外部 client response / error 変換
9. retry / timeout / 失敗時方針
10. event / outbox 連携
11. integration 契約確認
12. 回帰

### 2. 項目表を作る

- `unit` と `integration` を分けて表へ落とす
- repository と external client を同じ観点で無理に埋めない
- 対象に不要な観点は省略してよい
- 省略した観点があれば補足へ短く書く

### 3. 項目表を修正する

- ユーザー指摘を受けたら、行を追加、削除、統合、分割する
- 修正時は「何を変えたか」を短く添える

### 4. テストコードを作る

- 承認済み項目表を source of truth として扱う
- `unit` は query interface や SDK client を差し替えて閉じる
- `integration` は本物の DB や test container 利用を許容する
- `integration` は build tag、実行コマンド、CI job などで分離できるなら、その前提を結果に明記する
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

- repository 実装:
  - `repository mapping`
  - `domain 再構成`
  - `永続化動作`
  - `query 条件`
  - `transaction 実装`
  - `排他制御 / version`
  - `event / outbox 連携`
  - `integration 契約確認`
  - `回帰`
- external client:
  - `外部 client request 変換`
  - `外部 client response / error 変換`
  - `retry / timeout / 失敗時方針`
  - `integration 契約確認`
  - `回帰`
- transaction manager:
  - `transaction 実装`
  - `integration 契約確認`
  - `回帰`

### 表の出し方

- 先に 1 行で対象と前提を書く
- その下に Markdown 表を置く
- 表の行は、基本として **`unit` を先、`integration` を後** にする
- 同じテスト種別の中では、**観点の分類順を優先** して並べる
- 表の下に、今回使った観点の意味を 1 行ずつ短く補足してよい
- 表の後に、**domain / usecase / infra の境界で除外した項目** があれば短く書く

### 観点の短い説明

- `repository mapping`: domain object を保存用の値へ正しく詰め替えること
- `domain 再構成`: DB row や ORM model から domain object を正しく復元すること
- `永続化動作`: save / find / delete / upsert が期待どおり動くこと
- `query 条件`: filter / sort / paging / lock 条件が正しく反映されること
- `transaction 実装`: commit / rollback の扱いが正しいこと
- `排他制御 / version`: 楽観ロックや version 比較が仕様どおり機能すること
- `外部 client request 変換`: 内側の抽象入力を SDK / HTTP request へ正しく変換すること
- `外部 client response / error 変換`: 外部 response や error を内側向け表現へ正しく変換すること
- `retry / timeout / 失敗時方針`: 通信都合の制御が adapter の責務として正しいこと
- `event / outbox 連携`: 保存後の event publish や outbox 追加が期待どおり行われること
- `integration 契約確認`: 実 DB や実 API 契約と実装が食い違っていないこと
- `回帰`: 過去の ORM / SQL / client バグが再発しないこと

## コード生成のルール

- 先に表との対応関係を確認する
- `unit` と `integration` を同じファイルへ雑に混ぜない
- 長時間テストや外部依存テストは、必要なら build tag や CI 分離を前提に配置する
- SQL 文や SDK 詳細に依存する assertion は infra 側へ閉じる
- domain object の不変条件そのものは infra test で再検証しすぎない
- test container や実 DB が必要な場合は、その前提を結果に明記する

## してはいけないこと

- いきなりテストコードを書き始めること
- `unit` と `integration` の境界を曖昧なまま項目表を作ること
- repository 実装テストで domain の業務ルール本体を書き始めること
- ORM model や generated type を内側へ返す設計を前提にテストを書くこと
- 実 DB でしか分からない話を `unit` で済ませたことにすること
- user approval 前に「表は仮でいいから」とコード化へ進むこと

## 回答テンプレート

### 観点整理を返すとき

1. **対象**: 何のインフラテストか
2. **前提**: どの情報を根拠にしたか
3. **観点整理**: 今回採用する観点一覧
4. **補足**: `unit` / `integration` の切り分け、除外した責務

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
2. `unit` と `integration` をどのファイルへ作るか示す
3. 実装後に、表の各観点をどこまでカバーしたかを短く報告する

## 追加資料

- インフラ層の責務とテスト境界: [../infra-layer/SKILL.md](../infra-layer/SKILL.md)
- Go での repository / client 実装: [../go-implementation/SKILL.md](../go-implementation/SKILL.md)
- 例: [examples.md](examples.md)
