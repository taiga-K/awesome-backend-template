# 例

## 例1: 値オブジェクト `Email`

前提:

- ユーザーは「メールアドレス値オブジェクトのテストを作りたい」と依頼
- `docs/domain` に形式要件は少なく、入力ルールはコードと依頼文から読む

項目表:

| No | 対象 | 観点 | 事前状態/入力 | 操作 | 期待結果 | 備考 |
|---|---|---|---|---|---|---|
| 1 | `Email` | 正常系 | `user@example.com` | `NewEmail` | 生成成功 | 基本ケース |
| 2 | `Email` | 異常系 | 空文字 | `NewEmail` | エラー | 必須制約 |
| 3 | `Email` | 異常系 | `userexample.com` | `NewEmail` | エラー | `@` 不足 |
| 4 | `Email` | 境界値 | `a@b.cd` | `NewEmail` | 生成成功 | 最小長の妥当値の例 |
| 5 | `Email` | 境界値 | 256 文字相当のメールアドレス | `NewEmail` | エラー | 上限超過の例 |
| 6 | `Email` | 正規化 | `  user@example.com  ` | `NewEmail` | trim 後の値で保持 | 仕様次第 |
| 7 | `Email` | 回帰 | 過去に通ってしまった不正形式 | `NewEmail` | エラー | 再発防止 |

補足:

- HTTP request のバリデーション仕様が主題なら `presentation` 側を優先する
- この例では `再構成` を省略している。`ReconstructEmail` のような復元経路がある場合だけ追加する

## 例2: 集約 `Order`

前提:

- `Order` は `pending`, `completed`, `cancelled` を持つ
- 合計金額と明細整合性は集約内で守る

項目表:

| No | 対象 | 観点 | 事前状態/入力 | 操作 | 期待結果 | 備考 |
|---|---|---|---|---|---|---|
| 1 | `Order` | 正常系 | 正常な明細と合計 | `NewOrder` | 生成成功 | 基本ケース |
| 2 | `Order` | 異常系 | 明細が空、または必須値不足 | `NewOrder` | エラー | 生成失敗 |
| 3 | `Order` | 異常系 | 明細合計と合計金額が不一致 | `NewOrder` | エラー | 整合性 |
| 4 | `Order` | 状態遷移 | `pending` | `Complete` | `completed` になる | 正常遷移 |
| 5 | `Order` | 状態遷移 | `completed` | `Complete` | エラー | 再完了禁止 |
| 6 | `Order` | 状態遷移 | `cancelled` | `Complete` | エラー | 禁止遷移 |
| 7 | `Order` | 状態遷移 | `completed` | `Complete` を再実行 | 状態を壊さない | 冪等性をこの観点で扱う例 |
| 8 | `Order` | 不変条件 | `pending` で整合した注文 | `Complete` | 合計金額と明細整合性が保たれる | 操作後確認 |
| 9 | `Order` | 再構成 | 永続化済みの正当データ | `ReconstructOrder` | 復元成功 | `New` と責務分離 |

補足:

- 決済 API 呼び出しや通知送信が絡むなら、その部分は `usecase` のテスト項目へ移す
- この例では `回帰` を省略している。過去不具合や仕様誤解があれば、回帰行を追加する
