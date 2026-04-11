# `internal/infra` の肥大化判断と分割

## いつ使うか

- `internal/infra` をどう切るか相談されたとき
- DB、Redis、外部 API client、repository をどう並べるか迷ったとき
- 技術要素ごとに切るべきか、責務ごとに切るべきか判断したいとき

## 基本原則

- 最初の分割軸は **技術要素** を第一候補にする
- その技術要素の内側で `repository`, `client`, `db`, `query_service` を切る
- `shared`, `common`, `util` は最後の手段にする
- domain や usecase の責務が見えたら、infra に抱え込まない

## 基本形

```text
internal/infra/
├─ mysql/
│  ├─ db/
│  ├─ repository/
│  └─ query_service/
├─ redis/
│  ├─ client.go
│  └─ repository/
└─ slack/
   └─ client.go
```

## 肥大化シグナル

- 1 技術要素の配下に repository と query と client が混ざって見通しが悪い
- generated code、接続設定、mapping、query helper が一箇所に集中する
- `common.go`, `misc.go`, `helper.go` が増える
- 複数 DB や複数外部 API の責務が 1 パッケージに混ざる

## 分割の考え方

### 技術要素で切るのが自然な場面

- MySQL と Redis で依存パッケージも責務も違う
- Slack と Mail で設定や失敗時の扱いが違う
- DB ごとに transaction や query 実装が変わる

### repository を内側へ切るのが自然な場面

- 同じ技術要素配下に複数 repository 実装がある
- repository test をまとまりで見たい
- query_service と repository を分けた方が読みやすい

### `query_service` を切るのが自然な場面

- read 性能要件が強く、集約のフル再構成が重い
- 参照系だけ別の SQL や view、検索 index を使いたい
- 更新系 repository の責務へ参照最適化が流れ込み始めた

注意点:

- `query_service` は read 最適化の逃がし先であって、更新系の整合性ルールの置き場ではない

## 避けたい構成

```text
internal/infra/
├─ repository/
├─ client/
├─ db/
└─ helper/
```

悪い理由:

- MySQL と Redis と外部 API が横並びで混ざる
- 技術要素ごとの設定や依存が追いにくい
- 新しい実装追加時に置き場所判断がぶれやすい

## 回答の出し方

1. 結論
2. 分割軸
3. 推奨ディレクトリ例
4. domain / usecase へ戻すべき責務
