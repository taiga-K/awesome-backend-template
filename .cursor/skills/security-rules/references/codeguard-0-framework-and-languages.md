# フレームワークと言語のガイド

- `rule_id`: `codeguard-0-framework-and-languages`
- 原題: `Framework & Language Guides`

プラットフォームごとにセキュアバイデフォルトのパターンを適用する。設定を堅牢化し、組み込みの保護を使い、よくある落とし穴を避ける。

### Django

- 本番では DEBUG を無効にし、Django と依存関係を更新する。
- `SecurityMiddleware`、クリックジャッキング用ミドルウェア、MIME スニッフィング対策を有効にする。
- HTTPS を強制（`SECURE_SSL_REDIRECT`）。HSTS を構成。安全な Cookie フラグ（`SESSION_COOKIE_SECURE`、`CSRF_COOKIE_SECURE`）。
- CSRF: `CsrfViewMiddleware` とフォームの `{% csrf_token %}`、適切な AJAX トークン処理を確保する。
- XSS: テンプレートの自動エスケープに任せる。信頼できる場合以外 `mark_safe` を避ける。JS には `json_script` を使う。
- 認証: `django.contrib.auth` を使う。`AUTH_PASSWORD_VALIDATORS` でバリデータを設定する。
- シークレット: `get_random_secret_key` で生成し、環境／シークレットマネージャに保管する。

### Django REST Framework（DRF）

- `DEFAULT_AUTHENTICATION_CLASSES` と制限的な `DEFAULT_PERMISSION_CLASSES` を設定する。保護されたエンドポイントに `AllowAny` を残さない。
- オブジェクトレベルの認可では常に `self.check_object_permissions(request, obj)` を呼ぶ。
- シリアライザ: 明示的に `fields=[...]`。`exclude` や `"__all__"` を避ける。
- スロットリング: レート制限を有効にする（ゲートウェイ／WAF でも可）。
- 不要な不安全な HTTP メソッドを無効にする。生 SQL を避け、ORM／パラメータ化を使う。

### Laravel

- 本番: `APP_DEBUG=false`。アプリキーを生成。ファイル権限を安全にする。
- Cookie／セッション: 暗号化ミドルウェアを有効にし、`http_only`、`same_site`、`secure`、短い寿命を設定する。
- 一括代入: `$request->only()`／`$request->validated()` を使い、`$request->all()` を避ける。
- SQLi: Eloquent のパラメータ化。動的識別子は検証する。
- XSS: Blade のエスケープに任せる。信頼できないデータに `{!! ... !!}` を使わない。
- ファイルアップロード: `file`、サイズ、`mimes` を検証。`basename` でファイル名をサニタイズする。
- CSRF: ミドルウェアとフォームトークンを有効にする。

### Symfony

- XSS: Twig の自動エスケープ。信頼できる場合以外 `|raw` を避ける。
- CSRF: 手動フローでは `csrf_token()` と `isCsrfTokenValid()` を使う。フォームにはデフォルトでトークンが含まれる。
- SQLi: Doctrine のパラメータ化クエリ。入力の連結はしない。
- コマンド実行: `exec`／`shell_exec` を避け、Filesystem コンポーネントを使う。
- アップロード: `#[File(...)]` で検証。公開領域の外に保存し、一意の名前にする。
- ディレクトリトラバーサル: `realpath`／`basename` を検証し、許可されたルート内に限定する。
- セッション／セキュリティ: 安全な Cookie と認証プロバイダ／ファイアウォールを構成する。

### Ruby on Rails

- 危険な関数を避ける:

```ruby
eval("ruby code here")
system("os command here")
`ls -al /` # （バッククォート内は OS コマンド）
exec("os command here")
spawn("os command here")
open("| os command here")
Process.exec("os command here")
Process.spawn("os command here")
IO.binread("| os command here")
IO.binwrite("| os command here", "foo")
IO.foreach("| os command here") {}
IO.popen("os command here")
IO.read("| os command here")
IO.readlines("| os command here")
IO.write("| os command here", "foo")
```

- SQLi: 常にパラメータ化する。LIKE パターンには `sanitize_sql_like` を使う。
- XSS: デフォルトの自動エスケープ。信頼できないデータに `raw` や `html_safe` を使わない。許可リスト付き `sanitize` を使う。
- セッション: 機密アプリでは DB バックのストア。HTTPS を強制（`config.force_ssl = true`）。
- 認証: Devise など実績のあるライブラリを使い、ルートと保護領域を構成する。
- CSRF: 状態を変える操作に `protect_from_forgery`。
- 安全なリダイレクト: 宛先を検証／許可リスト化する。
- ヘッダ／CORS: 安全なデフォルトを設定し、`rack-cors` は慎重に構成する。

### .NET（ASP.NET Core）

- ランタイムと NuGet を更新し、CI で SCA を有効にする。
- 認可: `[Authorize]` 属性。サーバー側チェック。IDOR を防ぐ。
- 認証／セッション: ASP.NET Identity。ロックアウト。Cookie は `HttpOnly`／`Secure`。短いタイムアウト。
- 暗号: パスワードは PBKDF2、暗号化は AES-GCM、ローカルシークレットは DPAPI。TLS 1.2 以上。
- インジェクション: SQL／LDAP はパラメータ化。許可リストで検証する。
- 設定: HTTPS リダイレクトを強制。バージョンヘッダを削除。CSP／HSTS／X-Content-Type-Options を設定する。
- CSRF: 状態を変える操作にアンチフォージェリトークン。サーバーで検証する。

### Java と JAAS

- SQL／JPA: `PreparedStatement`／名前付きパラメータ。入力の連結はしない。
- XSS: 許可リスト検証。信頼できるライブラリで出力をサニタイズ。文脈に応じてエンコードする。
- ログ: ログインジェクションを防ぐためパラメータ化ログ。
- 暗号: AES-GCM。安全なランダム nonce。キーをハードコードしない。KMS／HSM を使う。
- JAAS: `LoginModule` のスタンザを構成する。`initialize`／`login`／`commit`／`abort`／`logout` を実装する。認証情報を露出させない。公開／非公開の認証情報を分離する。Subject のプリンシパルを適切に管理する。

### Node.js

- リクエストサイズを制限する。入力を検証・サニタイズし、出力をエスケープする。
- `eval`、ユーザ入力付きの `child_process.exec` を避ける。ヘッダには `helmet`、パラメータ汚染には `hpp`。
- 認証エンドポイントをレート制限する。イベントループの健全性を監視する。捕捉されない例外をきれいに処理する。
- Cookie: `secure`、`httpOnly`、`sameSite` を設定する。`NODE_ENV=production` にする。
- パッケージを更新し、`npm audit` を実行する。セキュリティリンターと ReDoS テストを使う。

### PHP の設定

- 本番の php.ini: `expose_php=Off`、エラーは表示せずログ。`allow_url_fopen`／`include` を制限。`open_basedir` を設定する。
- 危険な関数を無効化する。セッション Cookie にフラグ（`Secure`、`HttpOnly`、`SameSite=Strict`）を設定し、厳格なセッションモードを有効にする。
- アップロードのサイズ／個数を制限する。リソース上限（メモリ、POST サイズ、実行時間）を設定する。
- Snuffleupagus などで追加の堅牢化を行う。

### 実装チェックリスト

- 各フレームワークの組み込み CSRF／XSS／セッション保護と安全な Cookie フラグを使う。
- すべてのデータアクセスをパラメータ化する。信頼できない入力で危険な OS／exec 関数を使わない。
- HTTPS／HSTS を強制し、安全なヘッダを設定する。
- シークレット管理を一元化する。シークレットをハードコードしない。本番でデバッグを無効にする。
- リダイレクトと動的な識別子を検証／許可リスト化する。
- 依存関係とフレームワークを更新し、SCA と静的解析を定期的に実行する。
