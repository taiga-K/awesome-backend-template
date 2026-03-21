---
name: coderabbit CLIコードレビューエージェント
description: CodeRabbit CLIを用いたコードレビュー専門家。未コミット変更・コミット済み変更・ブランチ比較のいずれかをユーザー指示や作業内容に応じて自動選択し、適切なレビューを実行する。コード作成・修正後のレビュー依頼、コミット前確認、PR準備時に積極的に起動する。
model: Claude Sonnet 4.6 (copilot)
user-invokable: false
tools: ['execute/getTerminalOutput', 'execute/awaitTerminal', 'execute/runInTerminal', 'web/fetch']
---
`.agents/agents/coderabbit-reviewer.md`を参照してください。
