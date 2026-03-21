---
name: code-review-report
description: このスキルは、ユーザーが「コードレビュー報告書を作成する」「レビュー報告書を生成する」「レビュー結果をJSONに保存する」「レビューJSONファイルを作成する」と指示した場合、またはコードレビュープロセスが結果を `code-review-report-<yyyymmddHHMMSS>.json` ファイルに出力する必要がある場合に使用します。
---

# Code Review Report Generator

Generate a timestamped code review report JSON file in the format `code-review-report-<yyyymmddHHMMSS>.json`.

## Overview

This skill handles the creation of code review report files with dynamically generated timestamps. The report file is placed under `docs/reviews/` directory and follows a standardized JSON schema.

## Generating the Report Filename

To generate the filename with the correct timestamp, execute the bundled script:

```bash
bash ${SKILL_DIR}/scripts/generate-report-filename.sh
```

This outputs a filename like `code-review-report-20260210143025.json`.

Alternatively, generate the timestamp inline:

```bash
FILENAME="code-review-report-$(date +'%Y%m%d%H%M%S').json"
```

## Report File Location

Save the report to:

```
docs/reviews/code-review-report-<yyyymmddHHMMSS>.json
```

Create the `docs/reviews/` directory if it does not exist before writing the file.

## Report JSON Schema

The report file must follow this structure:

```json
{
  "reports": [
    {
      "id": "連番で1から始まるユニークな識別子(例:1,2,3...)",
      "review": "<レビュー内容を日本語で記載>",
      "level": "info/warning/error/critical",
      "improvement": "改善提案がある場合は具体的に記載、ない場合はnull",
      "status": "未対応/対応不要/対応必須/対応中/対応済み(レポート作成時は未対応とする)",
      "reason": "対応しない場合、その理由を具体的に記載(レポート作成時はnull)"
    }
  ]
}
```

### Field Definitions

| Field | Type | Description |
|---|---|---|
| `id` | number | 連番で1から始まるユニークな識別子(例:1,2,3...) |
| `review` | string | レビュー内容（日本語） |
| `level` | enum | 重要度: `info`, `warning`, `error`, `critical` |
| `improvement` | string \| null | 改善提案。提案がなければ `null` |
| `status` | enum | `未対応` / `対応不要` / `対応必須` / `対応中` / `対応済み`。新規作成時は `未対応` |
| `reason` | string \| null | 対応しない場合の理由。新規作成時は `null` |

## Workflow

1. Generate the timestamp filename using the bundled script or inline command
2. Ensure `docs/reviews/` directory exists (`mkdir -p docs/reviews`)
3. Collect review results from all sources
4. Format the results into the JSON schema above
5. Write the JSON file to `docs/reviews/<generated-filename>`
6. Report the created file path to the user

## Scripts

- **`scripts/generate-report-filename.sh`** - Generate the timestamped filename. Execute via Bash and capture stdout to obtain the filename.
