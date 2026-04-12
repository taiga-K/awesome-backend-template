---
name: go-implementation
description: Provides reusable guidance for implementing and reviewing idiomatic Go code, with emphasis on clarity, simplicity, and maintainability across naming, error handling, control flow, types, interfaces, API design, packages, testing, comments, and concurrency. Use when designing Go code, reviewing Go changes or pull requests, improving code to be more idiomatic, or evaluating Go-specific trade-offs and review comments.
---

# Go 実装・レビュー

## いつ使うか

- Go の新規実装で、Go らしい書き方と設計判断を揃えたいとき
- Go の PR や差分をレビューし、バグ・保守性・慣用性の観点で確認したいとき
- 命名、エラー処理、interface 設計、`context`、テスト方針に迷ったとき
- 他言語流の書き方が混ざっていないか見直したいとき

## このスキルの狙い

- Go らしさを **Clarity / Simplicity / Productivity** を中心に判断し、保守しやすさはその結果として確認する
- 単なる文法チェックではなく、**読みやすさ、変更しやすさ、誤用しにくさ** を優先する
- 実装とレビューの両方で、**結論、理由、修正方針、残るリスク** を短く整理する

## 最初に確認する

1. いま必要なのは **新規実装** か **レビュー** か
2. 変更対象は **公開 API** か **内部実装** か、あるいは **CLI / HTTP handler / worker / library** のどれか
3. 呼び出し側が区別すべき失敗か、単に `err != nil` で十分か
4. `context.Context`、goroutine、channel、lock が絡むか
5. ゼロ値、nil、所有権、可変共有の扱いで事故が起きないか
6. テストで仕様を固定すべき変更か

## 基本原則

- **clever さより明瞭さを優先する**
- **正常系が左端に見える制御フローを保つ**
- **interface は小さく、必要になるまで作らない**
- **受け口では抽象を受けても、返り値では具体を返す**
- **ゼロ値で安全に使える設計を優先する**
- **エラーは値として扱い、必要な文脈だけを足す**
- **パッケージ境界と依存方向を保守性の中心に置く**
- **テストとコメントは利用者と将来の保守者のために書く**
- **並行処理は性能目的ではなく、責務分離とキャンセル制御込みで設計する**

## 進め方

### 1. 実装するとき

1. まず API、責務、パッケージ境界を決める
2. 次に命名、型、ゼロ値、エラー方針を決める
3. 必要なときだけ interface と並行処理を導入する
4. 最後にテスト、doc comment、Example の追加要否を確認する
5. 迷った論点は、該当する章の参照ファイルを開いてから決める

### 2. レビューするとき

1. 先に仕様違反、バグ、リーク、競合、誤用しやすい API を探す
2. 次にエラー処理、制御フロー、命名、責務分割を見る
3. 最後にテスト不足、コメント不足、改善提案を整理する
4. 指摘は **現象 → なぜ問題か → どう直すか** の順で返す

## 重点論点

- 命名とコメント: 読み手が意図を誤解しない名前と契約の伝え方を揃える
- エラーと制御フロー: 正常系を追いやすくし、失敗の扱いを API 契約として整える
- 型と API 設計: ゼロ値、具体型、抽象境界のバランスを取る
- パッケージとテスト: 依存方向、責務分割、継続的に守れるテストを確認する
- 並行処理: 終了条件、キャンセル、所有権が追える構造にする

## してはいけないこと

- 他言語の慣習をそのまま持ち込み、Go の読みやすさを崩すこと
- エラー、抽象化、並行処理を必要以上に複雑化すること
- 依存方向や責務分割を曖昧にしたまま実装を広げること
- テストとコメントを後回しにして、契約がコード外から読めなくなること

## 追加資料

- 命名: [references/naming.md](references/naming.md)
- エラー: [references/errors.md](references/errors.md)
- 分岐とループ: [references/control-flow.md](references/control-flow.md)
- 型とデータ構造: [references/types-and-data-structures.md](references/types-and-data-structures.md)
- インターフェースと API 設計: [references/interfaces-and-api-design.md](references/interfaces-and-api-design.md)
- パッケージ: [references/packages.md](references/packages.md)
- テスト: [references/testing.md](references/testing.md)
- コメント: [references/comments.md](references/comments.md)
- 並行処理: [references/concurrency.md](references/concurrency.md)
- 実装時チェックリスト: [references/implementation-checklist.md](references/implementation-checklist.md)
- レビュー時チェックリスト: [references/review-checklist.md](references/review-checklist.md)
- 使い方と例: [examples.md](examples.md)
