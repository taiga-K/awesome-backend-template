# 例

このファイルでは、インフラ層の相談で返す **横断的な回答例** を残す。

## OR マッパーを domain に持ち込みそうな例

**入力**

- ユーザー: `gorm.Model をそのまま Product に埋め込みたい`

**出力例**

```markdown
**結論**
それは避けた方がよいです。

**理由**
`gorm` の都合が domain に逆流し、ドメインモデルの形が永続化都合で歪みやすくなるためです。

**置き場所**
- domain: `Product`
- infra: `gorm` model と repository 実装

**注意点**
DB row から `ReconstructProduct()` で戻す形を検討してください。
```

## repository 実装の最小方針を返す例

**入力**

- ユーザー: `ProductRepository の実装はどこまでやる？`

**出力例**

```markdown
**結論**
repository 実装は、集約単位の保存・取得、DB row と domain object の詰め替えを担います。

**理由**
永続化の詳細を infra に閉じ込め、domain と usecase を ORM や SQL から守るためです。

**置き場所**
- interface: `internal/domain/product/repository.go`
- 実装: `internal/infra/mysql/repository/product_repository.go`
```

## 楽観ロックの扱いに迷う例

**入力**

- ユーザー: `version カラムは infra の都合だから domain へ置きたくない`

**出力例**

```markdown
**結論**
排他制御の実現方法は infra に閉じ込めつつ、必要なら最小限の version 表現だけ内側へ出す案を検討します。

**理由**
楽観ロックは永続化都合ですが、完全に隠し切れない場合があるためです。

**注意点**
- update 時の version 比較は infra 実装で行う
- domain に出す場合も意味を最小限にする
```

## 外部通知クライアントの例

**入力**

- ユーザー: `Slack 通知の実装はどこに置く？`

**出力例**

```markdown
**結論**
`NotificationClient` の抽象は内側、`SlackNotificationClient` の実装は infra に置くのが自然です。

**理由**
Slack SDK や webhook 実装詳細を usecase や domain に漏らさないためです。

**置き場所**
- 抽象: `domain` または `usecase` 側の port
- 実装: `internal/infra/slack/client.go`
```

## 保存後の domain event 発行に迷う例

**入力**

- ユーザー: `repository 保存後にイベントを publish するのはどこが責務？`

**出力例**

```markdown
**結論**
保存後の domain event 発行は、repository 実装か outbox 実装の責務として扱うのが自然です。

**理由**
broker SDK や publish 方法は実装詳細であり、domain や usecase に漏らしたくないためです。

**置き場所**
- domain: event の概念や蓄積
- infra: publish 実装、outbox 書き込み、message broker 接続

**注意点**
- 同期 publish か outbox かを先に決める
- SDK 型や message format を内側へ返さない
```

## `Repository` と `Client` の命名を分ける例

**入力**

- ユーザー: `ファイル保存も通知送信も全部 Repository にしたい`

**出力例**

```markdown
**結論**
rollback 特性が違うなら、同じ `Repository` 抽象に寄せない方がよいです。

**理由**
DB 永続化は transaction に乗せやすい一方、通知送信や外部保存は不可逆であることが多いためです。

**推奨**
- DB 永続化: `Repository`
- 通知送信: `Client` or `Gateway`
- 外部ファイル保存: `Storage`
```

## `internal/infra` の分割を返す例

**入力**

- ユーザー: `infra を repository と client で横切って分けるべき？`

**出力例**

```markdown
**結論**
まずは技術要素単位で分ける方が追いやすいです。

**推奨構成**
internal/infra/
├─ mysql/
│  ├─ db/
│  └─ repository/
├─ redis/
│  ├─ client.go
│  └─ repository/
└─ slack/
   └─ client.go

**注意点**
`repository/` や `client/` をトップレベルへ横断的に置くと、MySQL と Redis と外部 API が混ざりやすくなります。
```
