---
name: log-design-guidelines
description: "アプリケーションログ設計のガイドライン。Google Cloudまたはローカル環境での標準出力ベースのログを対象とし、Go言語（log/slog）での実装を前提とする。ログメッセージは日本語で記述し、キー名はOTel準拠の英語dot.caseを使用する。出典: Future Architect ログ設計ガイドライン (https://future-architect.github.io/arch-guidelines/documents/forLog/log_guidelines.html)。使用タイミング: (1) ログ出力処理を新規実装するとき、(2) 既存のログ出力をレビュー・改善するとき、(3) ログのキー名や出力項目を設計するとき、(4) Web APIやバッチのアクセスログを設計するとき、(5) ログレベルの使い分けを判断するとき、(6) ログのセキュリティ・マスキングを検討するとき、(7) ログコスト最適化を検討するとき、(8) 運用手順書と紐づくメッセージコードを設計するとき。キー命名規則、レイアウト、出力項目、出力ルール、メッセージ言語方針、セキュリティ、性能、費用を網羅。"
---

# log-design-guidelines

このスキル適用時は、必ず以下のファイルの内容を参照して実行する。

## 必須

**参照ファイル**: `.agents/skills/log-design-guidelines/SKILL.md`

実行開始時に上記ファイルを Read ツールで読み込み、記載の手順・ルール・リファレンスに従ってログ設計・実装を行う。SKILL.md 内で参照されている `references/` 配下のファイルも必要に応じて読み込むこと。
