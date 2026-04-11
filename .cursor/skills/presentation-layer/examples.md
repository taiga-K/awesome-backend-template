# 例

このファイルでは、プレゼンテーション層の相談で返す **横断的な回答例** を残す。

## domain object をそのまま返したい例

**入力**

- ユーザー: `Task エンティティをそのまま JSON にして返したい`

**出力例**

```markdown
**結論**
そのまま返すより、response DTO か view model に詰め替える方を優先した方がよいです。

**理由**
表示用の書式変換や JSON 都合が domain 側へ逆流しやすくなるためです。

**置き場所**
- `internal/presentation/task/response.go`
- 書式変換は response mapper 側
```

## request struct をそのまま usecase へ渡したい例

**入力**

- ユーザー: `Gin の request struct をそのまま CreateTaskUseCase に渡したい`

**出力例**

```markdown
**結論**
request struct は presentation に残し、usecase Input DTO に詰め替えて渡す方がよいです。

**理由**
framework 依存をユースケース層へ漏らさず、依存方向を保ちやすいためです。
```

## 表示用書式変換の例

**入力**

- ユーザー: `金額のカンマ区切りを DTO のメソッドでやりたい`

**出力例**

```markdown
**結論**
書式変換は presentation 側へ置いてください。

**理由**
Output DTO はユースケースの戻り値であり、表示の責務は持たせない方が保守しやすいです。

**実装案**
- `internal/presentation/shared/formatter.go`
- もしくは `response.go` 内の mapper
```

## API バリデーションと domain バリデーションの例

**入力**

- ユーザー: `required チェックを presentation に置くなら domain 側は不要？`

**出力例**

```markdown
**結論**
API 入力制約は presentation に置いてよいですが、domain 側の不変条件は残すべきです。

**理由**
presentation は API 仕様、domain は業務整合性を守る責務だからです。
```

## controller で複数 usecase を呼びたくなった例

**入力**

- ユーザー: `TaskController から CreateTaskUseCase と NotifyTaskUseCase を順に呼びたい`

**出力例**

```markdown
**結論**
controller から呼ぶ usecase はまず 1 つに保つ方がよいです。

**理由**
presentation の責務は入出力の橋渡しであり、複数 usecase の調停を持ち込むと fat controller になりやすいためです。

**代替案**
- usecase 側で調停する
- 複数 endpoint で繰り返すなら責務の明確な独立クラスへ切り出す
```

## ID 値オブジェクトだけ controller で組み立てたい例

**入力**

- ユーザー: `path parameter の taskId を TaskID にしてから usecase に渡したい`

**出力例**

```markdown
**結論**
原則は usecase 側での生成ですが、ID 値オブジェクトは例外として controller 生成を許容してよいです。

**条件**
- 生成時ロジックが単純
- 変換の意味合いが強い
- チームで許容条件を明文化する
```

## 共通 error handler の例

**入力**

- ユーザー: `500 エラーを各 handler で返すのがつらい`

**出力例**

```markdown
**結論**
framework 依存の共通 error handler を presentation に置くのがよいです。

**置き場所**
- `internal/presentation/settings/error_handler.go`

**役割**
- domain/usecase/unexpected error を HTTP response へ詰め替える
- endpoint ごとの重複を減らす
```
