# 例

このファイルでは、ユースケース層の相談で返す **横断的な回答例** を残す。

## 単一集約のルールをユースケース層へ置こうとしている例

**入力**

- ユーザー: `Task の完了条件を CompleteTaskUseCase に全部書こうと思う`

**出力例**

```markdown
**結論**
完了条件の本体は `Task` エンティティ側へ寄せた方がよいです。

**理由**
単一集約の状態遷移ルールなので、ユースケース層へ置くと別の入口から崩れやすくなります。

**ユースケース層に残すもの**
- 認可
- transaction
- repository 呼び出し
- Output DTO への変換
```

## 複数集約をまたぐ例

**入力**

- ユーザー: `注文確定時に在庫も引き当てたい`

**出力例**

```markdown
**結論**
まずはユースケース層で `Order` と `Stock` の調停を行うのが自然です。

**理由**
複数集約にまたがる処理順序と transaction 境界の判断が必要だからです。

**置き場所**
- `internal/usecase/order/place.go`
- 単一集約のルールは `internal/domain/order` と `internal/domain/stock`

**次の打ち手**
- この調停ロジックが複数ユースケースに繰り返し現れるなら、責務名ベースのドメインサービスやイベント化も検討します
```

## 外部 API と通知がある例

**入力**

- ユーザー: `保存後に決済 API を叩いて、成功したらメールしたい`

**出力例**

```markdown
**結論**
DB 保存、決済 API、メール送信の順序と失敗方針を先に固定してください。

**推奨**
1. transaction 内で主データを確定
2. transaction 外で決済 API
3. メールは非同期候補として切り出す

**注意点**
決済 API の成功が主業務完了条件なら、同期実行と再実行方針が必要です。
```

## Go の最小ユースケース例

**入力**

- ユーザー: `Go で CreateProductUseCase の形を見せて`

**出力例**

```markdown
**結論**
`Run(ctx, input)` を入口にした小さな struct で始めるのがよいです。

**置き場所**
- `internal/usecase/product/create.go`
- DTO は `internal/usecase/product/dto.go`

**ポイント**
- repository と tx は interface で受ける
- domain object の生成は `domain`
- HTTP status 変換は presentation 側
```

## ユースケースからユースケースを呼びたくなった例

**入力**

- ユーザー: `CreateTaskUseCase から NotifyTaskUseCase を呼びたい`

**出力例**

```markdown
**結論**
ユースケースから別ユースケースを直接呼ぶのは、まず避けた方がよいです。

**理由**
責務境界が曖昧になり、transaction と副作用順序の追跡が難しくなるためです。

**代替案**
- domain の共通ルールなら domain へ寄せる
- 副作用なら usecase 内 helper か非同期イベントへ分離する
```
