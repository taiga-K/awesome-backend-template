---
name: usecase-layer-test
description: This skill should be used for `internal/usecase`, use cases, transaction boundaries, authorization flow, side-effect ordering, output DTOs, usecase tests, ユースケース層テスト, and テスト項目表 in this repository. It organizes usecase test viewpoints, creates a table-first test case matrix from user requirements and relevant code or docs, revises the matrix based on feedback, and generates Go test code only after explicit approval.
---

# ユースケース層テスト

## いつ使うか

- `internal/usecase` のテストを新規作成したいとき
- usecase のテスト観点を整理したいとき
- 先に「ユースケース層テストで何を見るべきか」を決めてから項目表へ落としたいとき
- 認可、transaction、副作用順序、失敗時の扱いを含めてテスト設計したいとき
- 項目表をユーザーと合意してから Go のテストコードへ落としたいとき

## このスキルの対象

- このリポジトリの **DDD x クリーンアーキテクチャにおけるユースケース層テスト**
- `internal/usecase` 配下に置く Go のテスト
- usecase
- Input DTO / Output DTO
- transaction boundary
- usecase 固有の外部依存 port
- `docs/domain/usecase/` を根拠にしたユースケース流れの確認

このスキルは、単一集約の不変条件や値オブジェクト検証本体は主対象にしない。  
それらが主題なら `../domain-layer/SKILL.md` の判断を優先する。

## 期待する出力

- 第 1 段階では、**観点整理** を返す
- 第 2 段階では、**テスト項目表** を返す
- 第 3 段階では、ユーザー指摘を反映した **修正版の項目表** を返す
- 第 4 段階では、承認済み項目表に沿った **Go のテストコード** を作成する
- 各段階で、**対象、観点、前提、期待結果、境界の判断** を短く明示する

## 基本原則

- **先に観点整理、次に表、最後にコード**
- **ユースケース層テストはビジネス処理の流れ全体を検証する**
- **domain object はモックしない**
- **repository、tx、external client など外部依存はテストダブルで分離する**
- **副作用がないことではなく、副作用が正しく制御されていることを確認する**
- **認可、transaction、副作用順序、副作用未実行、出力DTO、エラー伝播を重視する**
- **domain の不変条件そのものをユースケース層で再検証しすぎない**
- **ユーザーの明示承認があるまで、テストコードは作らない**

## 最初に確認する

1. ユーザーが求めているのは **観点整理** か **項目表** か **コード生成** か
2. 対象は usecase、job 起動 usecase、command handler のどれか
3. 認可、transaction、副作用順序、外部依存失敗のどれが主題か
4. 複数 repository や外部 port をまたぐか
5. Output DTO を返すか、domain object / result struct を返すか
6. 既存実装や既存テストに stub、fake、spy の流儀があるか

必要情報が不足する場合は、推測で埋め切らず、前提を明示して確認する。

## 作業の入口

### 1. 観点を整理する

- まず `AGENTS.md` と `ARCHITECTURE.md` を確認する
- 必要に応じて `../usecase-layer/SKILL.md` と `../go-implementation/SKILL.md` を確認する
- 認可、DTO、戻り値、調停の境界が主題なら、必要に応じて `../usecase-layer/references/usecase-core.md` も確認する
- transaction や副作用順序が主題なら、必要に応じて `../usecase-layer/references/transactions-and-side-effects.md` も確認する
- ユーザー入力、添付ファイル、`@docs`、対象コードから材料を集める
- `docs/domain/usecase/` があるなら、項目表の前提にどのユースケース記述を根拠にしたか短く書く
- 次の観点セットを基準に、必要な観点だけを選ぶ

1. 正常系
2. 認可
3. 入力解釈
4. ドメイン呼び出し
5. repository 呼び分け
6. トランザクション
7. 副作用順序
8. 副作用未実行
9. 外部依存失敗
10. 出力DTO
11. エラー伝播
12. 回帰

非同期 job や command handler が主題なら、retry、冪等性、再実行条件、失敗後の再配送は  
`外部依存失敗` や `回帰` の補助観点として備考列や補足へ出してよい。

### 2. 項目表を作る

- まず観点を整理し、その後に Markdown 表へ落とす
- 対象に不要な観点は省略してよい
- 省略した観点があれば補足へ短く書く
- domain ルール本体までユースケースの項目表に入れない

### 3. 項目表を修正する

- ユーザー指摘を受けたら、行を追加、削除、統合、分割する
- 修正時は「何を変えたか」を短く添える

### 4. テストコードを作る

- 承認済み項目表を source of truth として扱う
- domain object は本物を使う
- repository、tx、external client、notifier、job enqueuer は stub / fake / spy で閉じる
- 呼び回数の細かい確認より、結果と副作用発生条件を優先する
- domain や infra の責務が混ざる場合は、コード化前に先に報告する

### 承認の判定

- 次段階へ進む条件は、**直前に提示した項目表に対する明示承認** があること
- 明示承認の例: `OK`, `いいよ`, `進めて`, `LGTM`, `これでテストコードを書いて`, `表はこれでよい`
- 表を修正したあとは、**修正版に対して改めて承認** を取る
- いきなりコード作成を求められても、直前の項目表が未承認なら、項目表を再提示または要約して確認する
- 承認が曖昧なら、コード化へ進まず 1 文で確認する

## 項目表の作り方

### 推奨カラム

次の列を基本形とする。

| No | 観点 | 事前状態/入力 | 実行 | 期待結果 | 備考 |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |

### 観点の使い分け

- create / register 系 usecase:
  - `正常系`
  - `認可`
  - `入力解釈`
  - `ドメイン呼び出し`
  - `repository 呼び分け`
  - `トランザクション`
  - `副作用順序`
  - `副作用未実行`
  - `外部依存失敗`
  - `出力DTO`
  - `エラー伝播`
  - `回帰`
- update / complete 系 usecase:
  - `正常系`
  - `認可`
  - `ドメイン呼び出し`
  - `repository 呼び分け`
  - `トランザクション`
  - `副作用順序`
  - `副作用未実行`
  - `エラー伝播`
  - `回帰`
- query 系 usecase:
  - `正常系`
  - `認可`
  - `入力解釈`
  - `repository 呼び分け`
  - `出力DTO`
  - `エラー伝播`
  - `回帰`
- job / command handler 系 usecase:
  - `正常系`
  - `認可`
  - `入力解釈`
  - `ドメイン呼び出し`
  - `repository 呼び分け`
  - `副作用順序`
  - `副作用未実行`
  - `外部依存失敗`
  - `エラー伝播`
  - `回帰`

### 表の出し方

- 先に 1 行で対象と前提を書く
- その下に Markdown 表を置く
- 表の行は、基本として **観点の分類順を優先** して並べる
- 表の下に、今回使った観点の意味を 1 行ずつ短く補足してよい
- 観点が強く重なる行は、無理に分けず統合してよい
- 表の後に、**domain / usecase / infra の境界で除外した項目** があれば短く書く

### 観点の短い説明

- `正常系`: ユースケース全体が期待どおり最後まで進むこと
- `認可`: 実行権限のない主体を適切に拒否すること
- `入力解釈`: Input DTO から必要情報を正しく扱うこと
- `ドメイン呼び出し`: 必要な domain object の生成・更新が行われること
- `repository 呼び分け`: 条件に応じて正しい repository / port を使うこと
- `トランザクション`: 成功時と失敗時で transaction 境界の扱いが正しいこと
- `副作用順序`: 保存、通知、イベント投入などが正しい順序で行われること
- `副作用未実行`: 前段で失敗したとき、後続副作用が走らないこと
- `外部依存失敗`: 外部 API や外部 port の失敗時挙動が仕様どおりであること
- `出力DTO`: 戻り値が usecase 境界として適切な形であること
- `エラー伝播`: domain error や usecase error を壊さず返すこと
- `回帰`: 過去の不具合や仕様誤解が再発しないこと

## コード生成のルール

- 先に表との対応関係を確認する
- domain object はモックしない
- repository、tx、external client はスタブ化、または fake / spy で差し替える
- 呼び順や呼び回数の確認は、本当に意味があるものだけに絞る
- presentation 向けの HTTP status 変換は usecase test に持ち込まない
- 途中失敗時の rollback や副作用未実行は優先して確認する

## してはいけないこと

- いきなりテストコードを書き始めること
- domain object までモック化すること
- ユースケース層で単一集約の不変条件を再検証しすぎること
- 副作用順序や失敗時方針を曖昧なまま項目表を作ること
- HTTP status や JSON 形式の都合を usecase の責務として扱うこと
- user approval 前に「表は仮でいいから」とコード化へ進むこと

## 回答テンプレート

### 観点整理を返すとき

1. **対象**: 何のユースケース層テストか
2. **前提**: どの情報を根拠にしたか
3. **観点整理**: 今回採用する観点一覧
4. **補足**: 除外した責務、未確定事項

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
2. どのファイルへ何のテストを作るか示す
3. 実装後に、表の各観点をどこまでカバーしたかを短く報告する

## 追加資料

- ユースケース層の責務とテスト境界: [../usecase-layer/SKILL.md](../usecase-layer/SKILL.md)
- Go での usecase 実装とテスト方針: [../go-implementation/SKILL.md](../go-implementation/SKILL.md)
- 例: [examples.md](examples.md)
