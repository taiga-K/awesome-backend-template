# コメント

## いつ開くか

- doc comment に何を書くべきか迷うとき
- コメントが多いのにコードが読みにくいとき
- Example や `doc.go` を追加すべきか確認したいとき

## 基本原則

- コメントは利用者と将来の保守者のために書く
- 名前やコードで表せることを繰り返さない
- **What** は doc comment、**How** は本文近く、**Why** は特に価値が高い

## 1. doc comment の原則

- export されたトップレベル名には doc comment を付ける
- doc comment は対象シンボル名で始まる完全な文にする
- 型は「何を表すか」、関数は「何をするか」と副作用を書く
- bool を返す関数では `reports whether` のような書き方を意識する

## 2. 過不足の判断

- 自明な処理説明は書かない
- 背景、制約、誤用しやすい点、意外な振る舞いを書く
- コメントでしか説明できないなら、まず設計や命名を見直す

## 3. doc と本文コメントの分担

- 利用者が知るべき契約は doc comment に書く
- バッファサイズや内部アルゴリズムの詳細は本文近くへ書く
- 並行安全性、`Close` 必須、nil 許容などは契約なので doc に載せる

## 4. Go Doc Comments 構文

- `//` の行コメントを使う
- package comment は `Package <name> ...` で始める
- 必要なら Doc Links や箇条書き構文を使う
- `Deprecated:` を書くなら代替も添える

## 5. Example テスト

- 公開 API の使い方は `Example` で示すのが強い
- doc 内の静的コード例は古くなりやすい
- 出力を固定できるなら `Output:`、できないならコンパイル例として置く

## 6. doc.go

- パッケージ全体の説明が長いときは `doc.go` を使う
- パッケージの責務や利用場面を最初に伝える
- 1〜2文で説明しづらいなら、責務の切り方も見直す

## レビュー観点

- export シンボルに doc comment があるか
- doc comment がシンボル名で始まっているか
- 実装詳細を利用者向け doc に書き過ぎていないか
- 並行安全性や cleanup 契約など重要情報が欠けていないか
- コメントが悪い命名や悪い設計の言い訳になっていないか

## 関連

- 命名とコメントの境界: [naming.md](naming.md)
- Example とテスト設計: [testing.md](testing.md)
- cleanup 契約の API 設計: [interfaces-and-api-design.md](interfaces-and-api-design.md)
