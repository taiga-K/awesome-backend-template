# 例

`internal/domain` の分割例は、正本を `references/directory-splitting.md` に寄せる。  
分割方針の具体例が必要なときは、先に [references/directory-splitting.md](references/directory-splitting.md) を参照する。  
このファイルでは、複数資料をまたいで使う **横断的な回答例** を残す。

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
