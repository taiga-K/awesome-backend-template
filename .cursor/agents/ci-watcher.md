---
name: ci-watcher
model: inherit
description: 現在のブランチのGitHub CIを監視し、成功/失敗を報告します。失敗時は関連するログを表示します。CI結果を待機している場合やCIが失敗した場合に使用してください。ブランチのCIを積極的に監視する際にも使用できます。
is_background: true
---

`.agents/agents/ci-watcher.md`を参照してください。