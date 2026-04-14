---
name: go-fix-modernize
description: Modernizes Go code with `go fix` in Go 1.26+ by previewing diffs, applying safe analyzer-based rewrites, and validating the result. Use when the user asks to modernize Go code, refresh older idioms, apply `go fix`, review `//go:fix inline`, or run a repository-wide modernization sweep.
---

# Go Fix Modernize

このスキルは、Go 1.26 以降の `go fix` を使って Go コードを安全にモダン化したいときに使う。

## いつ使うか

- ユーザーが `go fix` を使って古い Go の書き方を新しくしたいとき
- `interface{}` から `any`、古い loop、古い標準ライブラリ利用を機械的に整えたいとき
- `//go:fix inline` を使った移行や、その影響確認をしたいとき
- 振る舞いを変えない範囲で、Go コードの一括整備をしたいとき

## このスキルの狙い

- `go fix` を **いきなり全面適用せず、まず差分確認してから適用** する
- 手作業レビューではなく、**Go 1.26 の analyzer ベースの安全な変換** を優先する
- モダン化と仕様変更を混ぜず、**機械的な更新だけを小さく分離** する

## 事前確認

1. 対象は **機械的なモダン化** だけか
2. 対象スコープは **`./...` 全体** か **特定 package 群** か
3. 実行環境の Go が **1.26 以上** か
4. `go fix` 後に確認すべき **テスト / lint / build** は何か
5. `//go:fix inline` を使う変更なら、呼び出し側の diff まで確認できるか

`go fix` は便利だが、仕様変更や責務変更を置き換えるものではない。API 契約や業務仕様を変える変更なら、通常の設計・文書更新フローを優先する。

## 基本方針

- まず **`-diff` で提案差分を見る**
- 問題なければ同じスコープに **本適用** する
- 変更は **モダン化だけ** に絞り、機能追加やリファクタリングを混ぜない
- 適用後は **format / test / lint** で崩れがないことを確認する
- 変換理由が自明でない場合は、PR やコミット本文で **`go fix` による機械的更新** だと明記する

## 推奨ワークフロー

### 1. スコープを決める

- リポジトリ全体なら `./...`
- 特定領域だけなら `./internal/...` や `./pkg/...` のように package pattern で絞る
- 一度に広げすぎず、レビュー可能な差分量を保つ

### 2. まず差分を確認する

```bash
go fix -diff ./...
```

特定 package に絞る例:

```bash
go fix -diff ./internal/...
```

差分確認では、次を重点的に見る。

- 期待どおりに古い記法が置き換わっているか
- import の追加・削除が自然か
- 生成差分に仕様変更や可読性低下が紛れていないか
- `//go:fix inline` による呼び出し側展開が過剰でないか

### 3. 問題なければ適用する

```bash
go fix ./...
```

必要ならスコープを絞って適用する。

```bash
go fix ./internal/...
```

### 4. 仕上げを確認する

少なくとも次を行う。

```bash
go test ./...
```

変更した Go ファイルには必要に応じて `gofmt -w` をかける。プロジェクトで lint を使っているなら、既存の lint 手順も実行する。

## よくある使いどころ

- `interface{}` を `any` に置き換える
- `for i := 0; i < n; i++` を `for i := range n` に寄せる
- `sort` 系の古い書き方を `slices` 系へ寄せる
- 単純なラッパー関数を `//go:fix inline` で移行し、呼び出し側を書き換える

## `//go:fix inline` を扱うとき

- ライブラリや共有 package の移行支援として使う
- 旧 API を残したまま、呼び出し側を機械的に新 API へ寄せたいときに向く
- 可能なら `Deprecated` コメントも併記して、利用者に意図を伝える
- 本当に inline してよいか、呼び出し側の可読性と将来の移行計画を確認する

例:

```go
// Deprecated: Use NewFunc instead.
//go:fix inline
func OldFunc(s string) string {
	return NewFunc(s, true)
}
```

## 判断基準

### 積極的に使ってよいケース

- 機械的で反復的な置換が中心
- Go の流儀へ寄せることが目的
- 大量の単純修正を人手で書き換えるより `go fix` の方が安全

### 使いすぎない方がよいケース

- 業務仕様や API 契約まで一緒に変える変更
- DDD / Clean Architecture の責務再配置が主目的の変更
- 生成差分の意味を説明できないまま repo 全体へ当てる変更
- Go 1.26 未満の環境しか使えない変更

## レビュー観点

- 差分が `go fix` 起因の機械的更新だけに収まっているか
- import 整理や式変形で可読性が下がっていないか
- `inline` により意図しない public API 依存が増えていないか
- 適用範囲が広すぎてレビュー不能になっていないか
- テスト、build、lint の結果が更新後も妥当か

## してはいけないこと

- `-diff` を見ずにいきなり repo 全体へ適用すること
- モダン化と機能追加を同じ変更に混ぜること
- Go バージョン前提を確認せずに `go fix` を前提化すること
- `//go:fix inline` を付けたのに、呼び出し側の影響確認を省くこと

## 返答のしかた

このスキルを使って作業する場合は、次の順で簡潔に返す。

1. 対象スコープと Go 1.26 前提を確認する
2. `go fix -diff` の要点を要約する
3. 問題なければ `go fix` を適用する
4. 最後に format / test / lint の結果を伝える

## 追加資料

- Go 1.26 の `go fix` 概要と modernize / inline の実例: https://future-architect.github.io/articles/20260129a/
