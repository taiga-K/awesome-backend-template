---
name: go-best-practices
description: "Go言語のベストプラクティスを網羅的にまとめたスキル。慣用的で読みやすく保守性の高いGoコードを書くための指針。3つの権威的なソースに基づく: Effective Go (go.dev/doc/effective_go)、Go Code Review Comments (go.dev/wiki/CodeReviewComments)、Google Go Style Guide (google.github.io/styleguide/go/)。使用タイミング: (1) 新しいGoコードを書くとき、(2) Goコードをレビューするとき、(3) Goコードをリファクタリングするとき、(4) Goのスタイルやイディオムの問題をデバッグするとき、(5) 命名、エラー処理、並行処理、インターフェース設計の判断をするとき、(6) Goテストを書く・改善するとき、(7) Goパッケージやプロジェクトを構成するとき。フォーマット、命名、制御フロー、関数、データ構造、インターフェース、並行処理、エラー処理、テスト、ドキュメンテーションを網羅。"
---

# Go ベストプラクティス

以下の3つの権威的なソースに基づく慣用的Goの指針:
- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Google Go Style Guide](https://google.github.io/styleguide/go/)

## リファレンスファイル

詳細なガイドラインはトピック別に分割。作業に関連するファイルを参照すること。

- **[references/naming.md](references/naming.md)** — パッケージ名、変数名、レシーバ名、頭字語、MixedCaps、ゲッター、インターフェース名、定数、重複回避
- **[references/formatting-and-style.md](references/formatting-and-style.md)** — gofmt、行の長さ、インポート、セミコロン、波括弧、複合リテラル、宣言、nilスライス
- **[references/control-flow.md](references/control-flow.md)** — if/for/switchのイディオム、エラーフローのインデント、range、型スイッチ、ラベル
- **[references/functions-and-methods.md](references/functions-and-methods.md)** — 複数戻り値、名前付き結果、defer、ポインタvsバリューレシーバ、レシーバ型の選択、値渡しvsポインタ渡し
- **[references/interfaces-and-types.md](references/interfaces-and-types.md)** — インターフェース設計、埋め込み、型アサーション、型変換、ジェネリクス
- **[references/error-handling.md](references/error-handling.md)** — errorインターフェース、エラー文字列、ラッピング（%v vs %w）、センチネルエラー、Don't Panic、recover、帯域内エラー、エラーログ
- **[references/concurrency.md](references/concurrency.md)** — ゴルーチン、チャネル、通信による共有、ゴルーチンの生存期間、同期関数、並列化、selectパターン
- **[references/testing.md](references/testing.md)** — テーブル駆動テスト、テスト失敗メッセージ、アサートライブラリ、cmpパッケージ、サブテスト、テストヘルパー、エラーのセマンティクス、テストダブル
- **[references/documentation.md](references/documentation.md)** — ドキュメントコメント、パッケージコメント、コメント文、サンプルコード、godoc規約

## クイックリファレンス: 5つのスタイル原則

1. **明確性（Clarity）** — コードの目的と根拠が読み手に明確
2. **簡潔性（Simplicity）** — 上から下へ読め、不要な抽象化を避ける
3. **簡明性（Concision）** — 信号対雑音比が高い
4. **保守性（Maintainability）** — 将来の修正が正しく行いやすい
5. **一貫性（Consistency）** — コードベース全体で似たコードと同じ見た目・振る舞い

## クイックリファレンス: 最頻出レビュー指摘事項

```go
// gofmt / goimports を全コードに実行する
// MixedCapsを使う。アンダースコアは使わない（maxLength であって max_length ではない）
// 頭字語: URL であって Url ではない、ID であって Id ではない、HTTP であって Http ではない
// コメント文: 対象の名前で始め、ピリオドで終える
// エラー文字列: 小文字で始め、句読点を付けない
// 全てのエラーを処理する — _ で捨てない
// エラーフローをインデント: エラーを先に処理し、正常パスはインデントしない
// 空スライス宣言: var t []string（t := []string{} ではない）
// 鍵生成には crypto/rand を使う。math/rand は使わない
// Contextは第1引数: func F(ctx context.Context, ...)
// 構造体のフィールドにContextを追加しない
// インターフェースは利用側パッケージに定義する（実装側ではない）
// 非同期より同期関数を優先する
// レシーバ名: 短く（1-2文字）、一貫性を保つ、"this"/"self" は使わない
// *string や *io.Reader を渡さない。値を直接渡す
// ゴルーチンの生存期間を明確にする — いつ終了するかドキュメントする
```
