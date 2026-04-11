# `internal/usecase` の肥大化判断と分割

## いつ使うか

- `internal/usecase` や `internal/application` をどう切るか相談されたとき
- ユースケース層が肥大化しているかを判断したいとき
- 共通化 helper を増やすべきか迷ったとき

## 基本原則

- 最初の分割軸は **ユースケース単位** にする
- `service/`, `common/`, `util/` を最初からトップレベルに置かない
- 共通化より、各ユースケースを追いやすいことを優先する
- ドメインの責務が見えたら、ユースケース層ではなく domain へ戻す

## 基本形

```text
internal/usecase/
├─ product/
│  ├─ create.go
│  ├─ get.go
│  └─ dto.go
└─ order/
   ├─ place.go
   └─ dto.go
```

## 肥大化シグナル

- 1 ユースケースが 1 ファイルで追えない
- 認可、トランザクション、副作用順序、出力整形が 1 箇所に混ざり過ぎる
- 同じ前処理や後処理が 3 回以上複製される
- `helper.go`, `common.go`, `misc.go` が増える
- ドメイン知識をユースケース層で持ち始める

## 分割の考え方

### まだ分けなくてよい

- ユースケース数が少ない
- 各 `Run()` が短く責務も明確
- 共通化候補がまだ抽象化しきれていない

### 分けた方がよい

- 同一ユースケース群に Input/Output DTO が複数あり見通しが悪い
- 同じ業務群のユースケースをまとめて読みたい
- 認可や副作用処理の補助 struct が増えた

### それでも共通化しすぎない

- `base_usecase.go` のような継承的共通化は避ける
- 汎用 helper に寄せる前に、単なる重複か、安定した共通概念かを確認する

## 判断例

### 良い例

```text
internal/usecase/
└─ task/
   ├─ create.go
   ├─ complete.go
   ├─ assign.go
   └─ dto.go
```

### 悪い例

```text
internal/usecase/
├─ service/
├─ common/
├─ helper/
└─ task_usecase.go
```

悪い理由:

- 何がユースケース単位の責務か見えにくい
- 重複の逃がし先だけが先に増える
- 新規メンバーが入口を見失いやすい

## 回答の出し方

1. 結論
2. 分割軸
3. 推奨ディレクトリ例
4. domain に戻すべき責務
