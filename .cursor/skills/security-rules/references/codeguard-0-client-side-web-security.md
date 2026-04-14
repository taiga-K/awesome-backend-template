# クライアントサイドの Web セキュリティ

- `rule_id`: `codeguard-0-client-side-web-security`
- 原題: `Client‑side Web Security`

ブラウザのクライアントを、コード注入、リクエスト偽造、UI のすり替え、クロスサイト情報漏えい、危険なサードパーティスクリプトから守るため、文脈を意識した多層的な制御を行う。

### XSS 対策（文脈に応じた対応）

- HTML 文脈: `textContent` を優先する。HTML が必要な場合は、審査済みライブラリ（例: DOMPurify）と厳格な許可リストでサニタイズする。
- 属性文脈: 属性は常に引用し、値をエンコードする。
- JavaScript 文脈: 信頼できない文字列から JS を組み立てない。インラインイベントハンドラを避け、`addEventListener` を使う。
- URL 文脈: プロトコル／ドメインを検証しエンコードする。不適切な場合は `javascript:` や data URL をブロックする。
- リダイレクト／フォワード: ユーザ入力を宛先に直接使わない。サーバー側のマッピング（ID→URL）か、信頼できるドメインの許可リストで検証する。
- CSS 文脈: 値は許可リスト化し、ユーザからの生のスタイル文字列を注入しない。

サニタイズの例:

```javascript
const clean = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ['b','i','p','a','ul','li'],
  ALLOWED_ATTR: ['href','target','rel'],
  ALLOW_DATA_ATTR: false
});
```

### DOM ベースの XSS と危険なシンク

- 信頼できないデータに対して `innerHTML`、`outerHTML`、`document.write` を禁止する。
- `eval`、`new Function`、文字列ベースの `setTimeout`／`Interval` を禁止する。
- `location` やイベントハンドラプロパティに代入する前にデータを検証・エンコードする。
- strict mode と明示的な変数宣言により、DOM クロバリングによるグローバル名前空間の汚染を防ぐ。
- Trusted Types を採用し厳格な CSP を適用して、DOM シンクの悪用を防ぐ。

Trusted Types + CSP:

```http
Content-Security-Policy: script-src 'self' 'nonce-{random}'; object-src 'none'; base-uri 'self'; require-trusted-types-for 'script'
```

### Content Security Policy（CSP）

- ドメイン許可リストより、nonce ベースまたはハッシュベースの CSP を優先する。
- まず Report-Only モードで違反を収集し、その後に強制する。
- 目指すベースライン: `default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'self'; form-action 'self'; object-src 'none'; base-uri 'none'; upgrade-insecure-requests`。

### CSRF 対策

- まず XSS を修正し、その上で CSRF 対策を重ねる。
- フレームワーク標準の CSRF 保護と、状態を変えるすべてのリクエストでの同期トークンを使う。
- Cookie 設定: `SameSite=Lax` または `Strict`、セッションは `Secure` と `HttpOnly`、可能なら `__Host-` プレフィックスを使う。
- Origin／Referer を検証する。SPA のトークンモデルでは API の変更操作にカスタムヘッダを要求する。
- 状態変更に GET を使わない。POST／PUT／DELETE／PATCH のみでトークンを検証する。トークン送信はすべて HTTPS で行う。

### クリックジャッキング対策

- 主手段: `Content-Security-Policy: frame-ancestors 'none'` または具体的な許可リスト。
- レガシーブラウザ向けフォールバック: `X-Frame-Options: DENY` または `SAMEORIGIN`。
- フレームが必要な場合は、機密操作に UX 上の確認を検討する。

### クロスサイト情報漏えい（XS-Leaks）の制御

- `SameSite` Cookie を適切に使い、機密操作には `Strict` を優先する。
- Fetch Metadata 保護を採用し、不審なクロスサイトリクエストをブロックする。
- 閲覧コンテキストを分離する。該当する場合は COOP／COEP および CORP を使う。
- キャッシュを無効化し、機密レスポンスにユーザ固有トークンを付与してキャッシュプロービングを防ぐ。

### サードパーティの JavaScript

- 最小化と分離: `sandbox` 付き iframe と postMessage の origin 検証を優先する。
- 外部スクリプトに Subresource Integrity（SRI）を使い、変更を監視する。
- ファーストパーティでサニタイズしたデータ層を用意し、可能ならタグから直接 DOM に触れさせない。
- タグマネージャの制御とベンダ契約で統制し、ライブラリを更新し続ける。

SRI の例:

```html
<script src="https://cdn.vendor.com/app.js"
  integrity="sha384-..." crossorigin="anonymous"></script>
```

### HTML5、CORS、WebSocket、ストレージ

- postMessage: 常に正確なターゲット origin を指定し、受信時に `event.origin` を検証する。
- CORS: `*` を避け、origin を許可リスト化する。プリフライトを検証し、認可を CORS に頼らない。
- WebSocket: `wss://` を要求し、origin 検証、認証、メッセージサイズ上限、安全な JSON パースを行う。
- クライアントストレージ: `localStorage`／`sessionStorage` に秘密を置かない。HttpOnly Cookie を優先する。やむを得ない場合は Web Worker で分離する。
- リンク: 外部の `target=_blank` には `rel="noopener noreferrer"` を付ける。

### HTTP セキュリティヘッダ（クライアントへの影響）

- HSTS: どこでも HTTPS を強制する。
- X-Content-Type-Options: `nosniff`。
- Referrer-Policy と Permissions-Policy: 機密なシグナルと機能を制限する。

### AJAX と安全な DOM API

- 動的なコード実行を避け、文字列ではなく関数コールバックを使う。
- JSON は `JSON.stringify` で組み立て、文字列連結で組み立てない。
- 生の HTML 挿入より、要素を生成して `textContent` や安全な属性を設定することを優先する。

### 実装チェックリスト

- すべてのシンクに対する文脈に応じたエンコード／サニタイズ。ガードなしの危険 API は使わない。
- nonce と Trusted Types による厳格な CSP。違反の監視。
- 状態変更リクエストすべてに CSRF トークン。安全な Cookie 属性。
- フレーム保護の設定。XS-Leaks 緩和（Fetch Metadata、COOP／COEP／CORP）の有効化。
- SRI とサンドボックスによるサードパーティ JS の分離。審査済みデータ層のみ。
- HTML5／CORS／WebSocket の用法を堅牢化。Web ストレージに秘密を置かない。
- セキュリティヘッダを有効化し検証する。

### テスト計画

- 危険な DOM／API パターンの自動チェック。
- CSRF とクリックジャッキングの E2E テスト。CSP レポートの監視。
- XS-Leaks（フレーム数、タイミング、キャッシュ）とオープンリダイレクト挙動の手動プローブ。
