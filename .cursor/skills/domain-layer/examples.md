# 例

## `internal/domain` をまだ分けない例

```text
internal/domain/
└─ task/
```

使う条件:

- `task` 配下の概念が少ない
- 変更が少数ファイルに閉じる
- `model` と `service` を分けるとかえって追いにくい

## `internal/domain` を業務境界の内側で分ける例

```text
internal/domain/
└─ task/
   ├─ model/
   ├─ service/
   └─ repository/
```

使う条件:

- `task` 配下の責務が増えた
- レビュー時にモデル変更とルール変更を分けて見たい
- 同種ファイルが複数あり、直下に並べると見通しが悪い

## 分け方を間違えている例

```text
internal/domain/
├─ model/
├─ service/
└─ repository/
```

問題点:

- `task` と `user` の境界がぼやける
- 1 つの業務変更で複数ディレクトリを往復しやすい
- 集約の凝集より技術分類が前に出る

## `application` へ上げるべき例

状況:

- `task` の完了条件判定に加えて `user` の状態確認が必要
- さらに通知送信や永続化順序の調停も必要

判断:

- 集約横断の手順と副作用調停なので、まず `application` の責務を疑う
- `domain/service` に押し込まず、`application` から各集約と外部依存を調停する

## `docs/domain` から OpenAPI を起こすとき、まず確認を返す例

**入力**

- ユーザー: `docs/domain から OpenAPI を作って`

**期待する動き**

1. `docs/domain/usecase/**/*.puml` を読む
2. `docs/domain/uml/**/*.puml` を読む
3. `docs/domain/ubiquitous-language.md` を読む
4. 不足している API 設計判断を列挙する

**出力例**

```markdown
`docs/domain` から次は確定できます。

- Task の主要属性
- taskStatus は「未完了」「完了」
- userStatus は「活性」「非活性」
- 完了、延期、担当者設定の業務制約

一方で、次は `docs/domain` だけでは確定できません。

- path の命名
- action endpoint の表現
- `dueDate` を `date` にするか `date-time` にするか
- 認証、認可
- エラー形式
```

## API 設計スキルを参照する例

**入力**

- ユーザー: `OpenAPI の叩き台を出して`

**期待する動き**

- `docs/domain` から概念、操作、制約を抽出する
- path や HTTP メソッドは `api-design` スキルを参照する
- `api-design` に未定義の点があれば先に確認する
- 仮定を置いた場合は、その点を明示する

## スコープ外ユースケースを除外する例

**入力**

- ユーザー: `overview.puml に従って OpenAPI 化して`

**期待する動き**

- 破線スコープ内のユースケースを優先する
- 枠外のユースケースは自動では含めない
- 含める必要があるならユーザーに確認する
