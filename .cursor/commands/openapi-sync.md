# openapi

`docs/api` 配下の OpenAPI を変更したあと、Redocly CLI で lint と bundle を実行する。`CONTRIBUTING.md` の「ドキュメント更新」と同じ手順である。

## 前提

- リポジトリのルートで実行する（`redocly.yaml` と `docs/api/openapi.yaml` が相対パスで解決できること）。

## 手順

### 1. Lint

```bash
npx @redocly/cli lint --config redocly.yaml docs/api/openapi.yaml
```

- エラーが出た場合は修正してから次へ進む。

### 2. Bundle（単一ファイルへ統合）

```bash
npx @redocly/cli bundle docs/api/openapi.yaml --output docs/api/api_schema.yaml
```

- `docs/api/api_schema.yaml` をコミット対象に含める（Pull Request 前に差分がないことを確認する）。

## 補足

- CI（`.github/workflows/openapi.yml`）でも同様に lint と bundle が走り、`api_schema.yaml` の更新漏れは失敗する。
