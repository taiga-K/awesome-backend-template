---
name: log-design
description: Defines application log design rules for this repository, including structured JSON Lines, OpenTelemetry/ECS-aligned keys, Go slog usage, Gin middleware and access logging, log levels, startup/batch logging, security, and cost control. Use when designing, implementing, or reviewing backend logs, Gin access logs, structured logging fields, or slog output in this repository.
---

# ログ設計

## いつ使うか

- Go / Gin / `slog` のログ出力方針を決めるとき
- Web API、バッチ、起動ログの項目や粒度を設計するとき
- 構造化ログのキー名、ログレベル、メッセージ規約を揃えるとき
- ログ実装やレビューで、可観測性、運用性、セキュリティ、費用を確認するとき

## 基本方針

- アプリログは `stdout` を基本にする
- デプロイメント環境では JSON Lines の構造化ログを基本にする
- キー名は OpenTelemetry を優先し、不足は ECS の語彙を取り入れる
- アプリコードにはベンダ固有キーを持ち込まず、必要な変換は収集基盤側に寄せる
- `message` は事実だけを書き、可変値は属性へ分離する
- 調査に必要な識別子を出しつつ、機密情報は出さない
- ノイズを減らしつつ、障害調査に必要なログは削らない

## 最初に決める

1. 対象ログは、起動、Web API、バッチ、例外、業務イベントのどれか
2. 主な読者は、開発者、運用者、監査、SRE の誰か
3. 全ログ共通の必須項目と、文脈ごとの拡張項目
4. ログレベルと、環境ごとの出力方針
5. `trace_id`、メッセージコード、通知要否を持たせるか
6. ミドルウェアや共通処理で自動付与する項目と、業務コードで明示出力する項目の境界

## このリポジトリでのデフォルト

- バックエンドは Go + Gin + `slog`
- 可変値は `slog` の属性で渡し、文字列連結しない
- `trace_id`、`request.id`、ユーザー識別子などは、できるだけミドルウェアや共通処理で自動付与する
- Web API のアクセスログはハンドラ内でばらばらに出さず、ミドルウェアで一元化する
- 起動ログは可読性優先、通常運用ログは分析性優先で設計する

## 進め方

1. 先に共通スキーマを決める
2. 次に HTTP、DB、例外、バッチなどの拡張項目を決める
3. その後にメッセージ文面、ログレベル、通知条件を揃える
4. 最後にセキュリティ、性能、費用、運用導線を点検する
5. 迷ったら参照資料を開いて、最小限のルールで統一する

## してはいけないこと

- `message` に ID や可変値を埋め込むこと
- パスワード、トークン、カード番号、PII をそのまま出すこと
- ヘルスチェックやループ処理で大量の低価値ログを出すこと
- ユーザー向けメッセージと開発者向けログを混在させること
- ベンダ固有キーをアプリコードへ直接埋め込むこと

## 追加資料

- 原則と決め方: [references/principles.md](references/principles.md)
- スキーマとキー名: [references/schema-and-fields.md](references/schema-and-fields.md)
- 種別ごとの出力ルール: [references/output-rules.md](references/output-rules.md)
- レビュー観点: [references/review-checklist.md](references/review-checklist.md)
- 例: [examples.md](examples.md)
