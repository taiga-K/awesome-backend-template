# バリデーションと例外ハンドリング

## いつ使うか

- API 入力制約をどこでチェックするか決めたいとき
- domain の不変条件と request validation の境界を整理したいとき
- 共通 error handler や error response 方針を決めたいとき

## 基本方針

- API 仕様として公開する入力制約は presentation でチェックしてよい
- domain の不変条件は domain で必ず守る
- 重複バリデーションはあり得るが、責務を混同しない
- 想定外エラーは presentation の共通 handler で client 向けに詰め替える

## プレゼンテーション層で扱うバリデーション

- required / optional
- 最大文字数
- JSON 形式
- path/query/body の基本整形
- API 仕様として外部公開している制約

## domain 側で必ず扱うもの

- 業務ルール
- 状態遷移制約
- 整合性の保証
- 別入口から来ても壊してはいけない制約

## 重複の考え方

- presentation 側に置くメリット:
  - API 仕様として明示できる
  - 早い段階で 400 を返せる
- デメリット:
  - domain 側と重複しやすい
  - 仕様変更時に修正漏れが起きやすい

## 共通 error handler

- framework 依存の共通 handler は presentation に置く
- domain error、usecase error、unexpected error を client 向け response に変換する
- HTML なら error page、JSON API なら error response object を返す

## 認証エラー

- 認証ライブラリ固有の失敗は presentation で扱う
- usecase へは、認証済みの抽象情報だけを渡す

## 避けたいこと

- domain error をそのまま framework 固有形式で返す
- HTTP status の判断を usecase へ持ち込む
- presentation validation があるから domain validation を省略する

## 回答の出し方

1. どの制約を presentation で扱うか
2. domain に残す制約
3. error mapping の場所
4. 400 / 500 の切り分け
