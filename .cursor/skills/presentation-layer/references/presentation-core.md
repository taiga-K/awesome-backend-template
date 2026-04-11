# プレゼンテーション層の責務

## いつ使うか

- プレゼンテーション層の責務を切り分けたいとき
- controller、handler、presenter の役割分担を整理したいとき
- 書式変換、認証、request/response の責務を決めたいとき

## 基本方針

- プレゼンテーション層は、クライアントとアプリケーションの入出力を実現する
- request を usecase が扱える形へ変換し、usecase の結果をクライアント向けに返す
- UI、JSON、HTML、HTTP status、書式、見た目に関する知識は presentation に置く
- コントローラーから呼ばれる usecase はまず 1 つに保つ
- 複数の入口で繰り返す処理は、責務が明確なら presentation の独立クラスへ切り出す

## 置くもの

- controller / handler
- presenter / response mapper
- request struct
- response struct / view model
- 認証情報や session 情報の bridge
- routing 設定
- middleware
- API 仕様として公開する入力制約
- 共通 error response

## 置かないもの

- 単一集約の不変条件
- エンティティ内部の状態遷移
- repository 呼び出し順序そのものの設計
- ORM や SQL の詳細

## 表示用変換

- 数値の書式変換
- 日付フォーマット
- 表示用ラベル化
- UI 向け結合文字列

これらは presentation の責務。domain や usecase DTO に持ち込まない。

## 認証とセッション

- 認証方式やライブラリ固有の知識は presentation に閉じ込める
- usecase には「必要な情報だけ」を渡す
- 例: framework の認証結果を `UserSession` のような抽象情報へ変換して渡す

## 値オブジェクト生成の例外

- 原則として、エンティティや値オブジェクトの生成は usecase 側へ寄せる
- ただし ID を表す値オブジェクトは、ルールが明確で変換の意味合いが強いなら controller 生成を許容してよい
- この例外を使うなら、チームのルールとして明文化する

## domain object をそのまま返すか

- 原理上は可能でも、表示処理の逆流リスクが高い
- display 用メソッドを domain に生やしたくなるなら、response/view model に変換する
- チームで許容条件を明文化できないなら DTO / view model へ詰め替える方を優先する

## query service の扱い

- 読み取り専用の DTO を返す query service を使う構成はあり得る
- 原則は usecase 経由で呼ぶ説明を優先する
- ただしチーム規約で controller から query service を直接使うなら、その適用範囲を限定して明文化する
- query service の戻り値に表示用変換を混ぜず、response/view model への最後の詰め替えは presentation に残す

## controller と presenter を分けるか

- controller と presenter を分ける設計は有効
- ただし常に別クラスへ分離する必要はない
- handler 1 つに同居させる場合でも、request parsing と response formatting の責務を混ぜ過ぎない

## cron や定期実行

- cron や scheduler もユースケースの呼び出し元の一種として presentation 側で扱ってよい
- usecase の入出力をフレームワーク非依存にしておくと、HTTP でも cron でも再利用しやすい

## 回答の出し方

1. 結論
2. presentation に置く責務
3. domain/usecase に戻す責務
4. 置き場所
5. 注意点
