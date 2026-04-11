# `docs/domain` から `docs/api` へ落とす

## この資料が扱う範囲

- `docs/domain` から OpenAPI を起こす前提整理
- ドメイン文書から何を抽出するか
- 不足情報の確認方法
- `docs/api` へ保存するときの分割構成

API の path、HTTP メソッド、エラー設計、認証方式、レスポンス形式などの **Web API 設計判断** は、必要に応じて `../../api-design/SKILL.md` を併読する。

## いつ使うか

- ユーザーが `docs/domain` から OpenAPI または Swagger を作りたい
- ユースケース図やドメインモデル図から API の叩き台を起こしたい
- ドメイン文書から endpoints、schemas、errors を整理したい
- `docs/api` 配下へ OpenAPI をファイルとして作成したい

## 既定方針

- **既定は確認優先**: `docs/domain` にない API 設計判断は、勝手に確定せず **不足点を列挙して先に確認**する
- **根拠を分ける**: 「文書に書かれていること」と「API として補った判断」を混ぜない
- **OpenAPI を正にする**: 出力は基本的に OpenAPI 3.1 の YAML を優先する
- **API 設計は別スキルに委譲する**: path、HTTP メソッド、action endpoint、エラー設計は `api-design` を参照する
- **`docs/api` に成果物を作るときは分割構成まで完成させる**

## 最初に確認する入力

最低限、次を **入力の棚卸しとして** 確認する。  
この段階は「何が存在するか」を把握するためのチェックであり、矛盾したときの優先順位そのものではない。

- `docs/domain/ubiquitous-language.md`
- `docs/domain/usecase/**/*.puml`
- `docs/domain/usecase/**/*.md`
- `docs/domain/uml/**/*.puml`
- 既存の API 文書やサーバ実装があるならそれも確認する

## 入力ソースの優先順位

ソース間で内容が食い違ったときは、次の順で判断する。

1. `docs/domain/usecase/*.puml` と `*.md`
2. `docs/domain/uml/*.puml`
3. `docs/domain/ubiquitous-language.md`
4. 既存 API 実装、既存仕様

矛盾したら、既存 API 実装またはユーザー確認を優先する。  
ただし、**食い違いを黙って解消しない**。

## `docs/domain` と実装が食い違うとき

### 結論

先に差分を列挙し、確認に回す。

### 手順

1. `docs/domain` と実装の差分を箇条書きで並べる
2. 差分を次の 3 区分で整理する
   - **`docs/domain` が古い**
   - **実装が古い**
   - **未確定で確認が必要**
3. 未確定のものは、OpenAPI の確定事項として書かない
4. 叩き台を作る場合も、差分一覧と仮定を別枠で明示する

### 例

```markdown
差分一覧:
- `docs/domain` では Task は `dueDate` 必須、実装では nullable
- `docs/domain` では taskStatus は 2 値、実装では `archived` が追加されている

区分:
- `docs/domain` が古い: taskStatus の値
- 未確定で確認が必要: `dueDate` の必須 / 任意
```

## 役割分担

- この資料は **`docs/domain` から何を抽出するか** を扱う
- path、HTTP メソッド、request / response 形、action endpoint、エラー設計は **`api-design` スキル**が扱う
- ここで扱うのは、ドメイン文書から得た概念、操作、制約を OpenAPI の材料へ変換すること

## 作業手順

1. **入力ソースを把握する**
   - `docs/domain` から、ユースケース、用語、モデル、ルールを集める
2. **ユースケースを API 候補へ変換する**
   - 例: 「タスクを作成する」 -> 作成 API 候補
3. **モデルを schema 候補へ変換する**
   - 属性、enum 候補、必須項目、関連を抽出する
4. **API 設計スキルを参照する**
   - path、HTTP メソッド、request / response 形、エラー設計は `api-design` に従う
5. **不足している API 設計判断を列挙する**
   - `api-design` と `docs/domain` だけで埋まらない点は、ユーザーに確認する
6. **OpenAPI 草案を作る**
   - `paths`, `components.schemas`, `components.responses` を中心に組み立てる
7. **仮定を明示する**
   - どうしても補完した箇所がある場合は、OpenAPI 本体とは別に assumptions を列挙する
8. **`docs/api` に書くときは分割構成へ落とし込む**
9. **Redocly で検証する**
   - `docs/api` に保存した成果物は、`.cursor/commands/openapi.md` の手順に従って lint と bundle を確認する

## ユースケースから operation 候補へ

まずはユースケースごとに「何の操作か」を整理する。

- `〜を作成する` は **作成操作**
- `〜を取得する` は **参照操作**
- `〜を更新する` は **更新操作**
- `〜を削除する` は **削除操作**
- `〜を完了する` や `〜を延期する` は **業務操作**

HTTP への落とし込み方は `api-design` に従う。

## ドメインモデルから schema へ

- クラス名は `components.schemas` の候補
- 代表属性は schema の `properties` 候補
- ノートの業務ルールは validation または説明文候補
- 「〜のみ」は enum 候補
- ID 参照は `string` 仮置きにせず、型未定として確認対象にしてよい

## 最低限確認すべき API 設計判断

- path 命名規約
- HTTP メソッド規約
- ID の型
- `date` / `date-time`
- 操作系 endpoint の表現
- レスポンス共通 envelope の有無
- エラー形式
- 認証、認可
- 一覧取得、検索、ページングの有無
- nullable の扱い

これらは `api-design` スキルまたはユーザー確認で埋める。

## 不足情報があるときの出し方

既定では、いきなり YAML を出し切らず、まず次の形で確認する。

```markdown
不足している API 設計判断:
- path 命名規約
- action endpoint の表現
- `dueDate` は `date` か `date-time` か
- 認証主体は誰か
- エラー形式

`docs/domain` から確定できること:
- Task の主要属性
- taskStatus の候補
- 担当者設定の業務制約
```

ユーザーが「叩き台でよい」「仮定つきで進めてよい」と言ったら、その時点で `api-design` の規約またはユーザー指示を使って YAML を作る。

## `docs/api` へ保存するときの既定

- 既定の成果物は **OpenAPI 3.1 YAML**
- `docs/api` にファイルとして作成、更新する場合は、**最初から分割構成**で扱う
- ルートの `docs/api/openapi.yaml` は entrypoint とし、path と schema の本体は外部ファイルへ分ける
- 分割は **必要最低限** にとどめ、最低でも `paths/` と `components/schemas/` を最初から作る
- `components/parameters/` や `components/responses/` などの追加ディレクトリは、実際に必要なときだけ作る
- API バージョンを URI に含める場合は、原則として `paths` に `/v1/...` を埋め込まず、`servers.url` 側のベースパスで表現する
- `paths` は常にベース URL からの相対リソースパスとして保ち、`/tasks` のように業務リソース中心で表現する
- 根拠のある仕様と、補完した仮定を混ぜない
- チャット上で YAML 草案を一時的に 1 ファイルで組み立てるのはよいが、`docs/api` に保存するときは単一ファイルのまま終えない

## 分割構成の既定

```text
docs/api/
├── openapi.yaml
├── paths/
│   ├── tasks.yaml
│   └── tasks_{taskId}_completion.yaml
└── components/
    └── schemas/
        ├── task.yaml
        └── create-task-request.yaml
```

`components/examples/` などは、実際に参照が発生してから追加する。  
`components/parameters/` や `components/responses/` は、必要な参照がある場合だけ追加してよい。

## バージョニング

- OpenAPI の `paths` は `servers.url` に対する相対パスとして扱う
- API バージョンを URI に含める場合、まず `servers.url: https://api.example.com/v1` のような表現を検討する
- `paths` には `/tasks`, `/tasks/{taskId}` のようなリソースパスを書く
- 同じ版の API を表す 1 つの OpenAPI 文書の中で、すべての path に `/v1` を繰り返し書かない

## 推奨出力構成

1. まず `docs/domain` から確定できること
2. 次に `api-design` で必要な API 設計判断
3. `api-design` またはユーザー確認後に OpenAPI YAML
4. 補った仮定の一覧
5. Redocly による検証結果、または未検証の理由

## Redocly による機械検証

`docs/api` に成果物を保存、更新した場合は、意味レビューだけで終わらせず **OpenAPI 文書として壊れていないこと** も確認する。

既定では `.cursor/commands/openapi.md` の手順に従い、次を確認する。

1. Lint

```bash
npx @redocly/cli lint --config redocly.yaml docs/api/openapi.yaml
```

2. Bundle

```bash
npx @redocly/cli bundle docs/api/openapi.yaml --output docs/api/api_schema.yaml
```

最低限の確認対象:

- `redocly.yaml` と `docs/api/openapi.yaml` が存在し、コマンド前提を満たしているか
- `$ref` が解決できるか
- 分割構成の entrypoint と生成される `docs/api/api_schema.yaml` が整合しているか
- lint で検出される構文、参照、必須記述の不備がないか

前提ファイルや手順が未整備で実行できない場合は、無理に「検証済み」とせず、**何が不足していて未検証なのか** を結果に明記する。

## レビュー観点

- ユースケースが operation に対応しているか
- ドメインルールが schema 説明やエラーに反映されているか
- enum がドメイン文書と矛盾していないか
- スコープ外ユースケースを混ぜていないか
- 仮定と確定事項が混ざっていないか
- path と HTTP メソッドが `api-design` に反していないか
- API バージョンが path に重複して埋め込まれず、`servers.url` と役割分担できているか
- schema 名、operation の責務、エラー表現が一貫しているか
- 不要な分割で探索コストを増やしていないか
- `docs/api` に保存された成果物が、単一ファイルではなく分割構成になっているか

## やってはいけないこと

- `docs/domain` にない仕様を、確定事項のように書かない
- ドメイン図の概念をそのまま HTTP 設計に直結させると決め打ちしない
- `api-design` にない認証、認可、エラー設計を無言で固定しない
- 既存 API 実装があるのに無視して新しい流儀を持ち込まない
- `docs/api` に成果物を作る依頼なのに、単一ファイル YAML のままで終えること
- 先回りでディレクトリ階層を増やしすぎること
- 1 つの概念を過剰に細分化して保守性を下げること
