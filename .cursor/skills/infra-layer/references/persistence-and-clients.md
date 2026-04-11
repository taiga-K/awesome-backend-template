# 永続化と外部クライアント

## いつ使うか

- OR マッパーの扱いを決めたいとき
- 楽観ロックや更新日時の責務を整理したいとき
- Slack、メール、外部 API client をどこに置くか決めたいとき

## OR マッパーの扱い

- OR マッパークラスは repository 実装の中でだけ使う
- 更新系では domain object を ORM/SQL 用 struct に詰め替えて保存する
- 参照系では DB の値を取得して domain object を再構成する
- domain や usecase に ORM の型を渡さない

## 再構成

- DB の値からインスタンスを再構成する専用の生成経路を使う
- repository 実装以外から再構成用 API を雑に呼ばせない
- 新規生成時の初期値と、DB 復元時の値を混ぜない

## 自動カラム

- `created_at`, `updated_at` など OR マッパー自動カラムの扱いは慎重に決める
- 画面表示や業務上意味のある時刻なら、domain 側で明示的に扱う選択もある
- ただし、更新タイミングの主導権が誰にあるかを先に決める

## 楽観ロック

- version カラムは永続化都合だが、完全に隠し切れない場合がある
- その場合でも、排他制御の **実現方法** 自体は infra に閉じ込める
- domain へ出すなら最小限の表現に留める
- 実際の update クエリで version 比較を行うのは infra 実装
- lock の **実現方法** は infra だが、必要なら repository interface に抽象的なロック意図を出してもよい
- その場合も `SELECT FOR UPDATE` のような DB 固有表現は内側へ持ち込まない

## domain event 発行

- 保存後に蓄積済み domain event を publish する責務は、repository 実装側へ置く選択肢がある
- event publish を同期実行するか、outbox へ積むかは infra の実装詳細として扱う
- usecase や domain に broker SDK や message format を漏らさない

## 外部クライアント

- domain/usecase が必要とする抽象は内側に置く
- Slack、メール、HTTP SDK の具体的な実装は infra に置く
- どの SDK を使うか、認証方法、endpoint、retry などは infra に閉じ込める
- ドメイン上で Slack が重要な概念なら名前を出してよいが、実現詳細は出さない

## 命名と rollback 特性

- DB 保存のように rollback 対象となる処理と、通知送信のように不可逆な処理は同じ抽象に寄せ過ぎない
- その差が重要なら `Repository` ではなく `Client`, `Gateway`, `Storage` のように分ける
- 命名は「何を扱うか」だけでなく、「transaction にどう乗るか」も反映させる

## read 側の逃がし先

- read 性能や検索要件が強いときは、集約 repository だけで解決しようとしない
- query model や `query_service` を使って、更新系と参照系を分けてよい
- ただし、更新時の業務整合性を query model 側で担わない

## 認証情報の境界

- ログイン中ユーザー情報の取得元詳細は presentation/infra 側の関心になりやすい
- usecase が必要とする認証情報の抽象だけを内側で扱う
- token 解析や framework session 依存は infra / presentation に留める

## 回答の出し方

1. 何を内側に残すか
2. 何を infra に閉じ込めるか
3. 再構成やロックの扱い
4. テスト観点
