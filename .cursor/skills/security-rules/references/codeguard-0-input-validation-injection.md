# 入力検証とインジェクション対策

- `rule_id`: `codeguard-0-input-validation-injection`
- 原題: `Input Validation & Injection Defense`

信頼できない入力は検証し、コードとして解釈されないようにすること。SQL、LDAP、OS コマンド、テンプレート、JavaScript ランタイムのオブジェクトグラフにまたがるインジェクションを防ぐこと。

### 中核となる方針
- 信頼境界で早期に、肯定（許可リスト）検証と正規化（canonicalization）を行うこと。
- 信頼できない入力はすべてデータとして扱い、コードとして扱ってはならない。コードとデータを分離する安全な API を用いること。
- クエリ／コマンドはパラメータ化すること。エスケープは最後の手段とし、文脈に応じて行うこと。

### 検証の実践手順
- 構文検証：各フィールドの形式、型、範囲、長さを強制する。
- 意味検証：業務ルールを強制する（例：開始日 ≤ 終了日、列挙の許可リスト）。
- 正規化：検証前にエンコーディングを正規化する。完全な文字列を検証する（正規表現は `^` と `$` でアンカーする）。ReDoS に注意する。
- 自由形式テキスト：文字クラスの許可リストを定義する。Unicode を正規化する。長さの上限を設ける。
- ファイル：コンテンツタイプ（マジック）、サイズ上限、安全な拡張子で検証する。ファイル名はサーバー側で生成する。スキャンする。Web ルート外に保存する。

### SQL インジェクションの防止
- データアクセスの 100% でプリペアドステートメントおよびパラメータ化クエリを用いる。
- ストアドプロシージャ内の動的 SQL 構築では、すべてバインド変数を用い、ユーザー入力を SQL に連結してはならない。
- 最小権限の DB ユーザーとビューを優先する。アプリアカウントに管理者権限を与えてはならない。
- エスケープは壊れやすく推奨されない。パラメータ化が主な防御である。

例（Java PreparedStatement）：
```java
String custname = request.getParameter("customerName");
String query = "SELECT account_balance FROM user_data WHERE user_name = ? ";  
PreparedStatement pstmt = connection.prepareStatement( query );
pstmt.setString( 1, custname);
ResultSet results = pstmt.executeQuery( );
```

### SOQL／SOSL インジェクション（Salesforce）

SOQL と SOSL はクエリ／検索言語であり（SQL スタイルの DDL／DML はない）。データ変更は Apex DML または Database メソッドで行う。注：SOQL は `FOR UPDATE` で行をロックできる。

- 主なリスク：意図したクエリフィルタや業務ロジックを迂回したデータ流出。Apex が昇格されたアクセス（システムモード）で動く場合や CRUD／FLS が強制されない場合、影響が増幅する。
- 二次的リスク（条件付き）：クエリ結果が DML に渡される場合、インジェクションがレコード集合を広げ、意図しない一括更新／削除を引き起こし得る。
- 静的 SOQL／SOSL とバインド変数を優先する：`[SELECT Id FROM Account WHERE Name = :userInput]` または `FIND :term`。
- 動的 SOQL には `Database.queryWithBinds()`、動的 SOSL には `Search.query()` を用いる。動的な識別子は許可リストで制限する。連結が避けられない場合は、`String.escapeSingleQuotes()` で文字列値をエスケープする。
- `WITH USER_MODE` または `WITH SECURITY_ENFORCED` で CRUD／FLS を強制する（両方は組み合わせない）。`with sharing` またはユーザーモード操作でレコード共有を強制する。DML の前に `Security.stripInaccessible()` を用いる。

### LDAP インジェクションの防止
- 常に文脈に応じたエスケープを適用する。
  - DN エスケープ：`\ # + < > , ; " =` および先頭／末尾のスペース
  - フィルタエスケープ：`* ( ) \ NUL`
- クエリ構築前に許可リストで入力を検証する。DN／フィルタエンコーダーを提供するライブラリを用いる。
- バインド認証を伴う最小権限の LDAP 接続を用いる。アプリケーションのクエリに匿名バインドを避ける。

### OS コマンドインジェクションの防御
- シェル実行より組み込み API を優先する（例：`exec` よりライブラリ呼び出し）。
- やむを得ない場合は、コマンドと引数を分離する構造化実行（例：ProcessBuilder）を用いる。シェルを起動してはならない。
- コマンドは厳格に許可リストとし、引数は許可リストの正規表現で検証する。メタ文字（`& | ; $ > < \` \ ! ' " ( )` および必要に応じて空白）を除外する。
- サポートされている場合は `--` で引数を区切り、オプションインジェクションを防ぐ。

例（Java ProcessBuilder）：
```java
ProcessBuilder pb = new ProcessBuilder("TrustedCmd", "Arg1", "Arg2");
Map<String,String> env = pb.environment();
pb.directory(new File("TrustedDir"));
Process p = pb.start();
```

### クエリのパラメータ化に関する指針
- プラットフォームのパラメータ化機能を用いる（JDBC PreparedStatement、.NET SqlCommand、Ruby ActiveRecord のバインド、PHP PDO、SQLx のバインドなど）。
- ストアドプロシージャではパラメータをバインドすること。プロシージャ内で文字列連結により動的 SQL を組み立ててはならない。

### プロトタイプ汚染（JavaScript）
- オブジェクトリテラルの代わりに `new Set()` または `new Map()` を用いること。
- オブジェクトが必要な場合は、`Object.create(null)` または `{ __proto__: null }` で作成し、継承されたプロトタイプを避ける。
- 不変にすべきオブジェクトは freeze または seal する。防御の深さとして Node の `--disable-proto=delete` を検討する。
- 安全でないディープマージユーティリティを避ける。キーを許可リストで検証し、`__proto__`、`constructor`、`prototype` をブロックする。

### キャッシュと転送
- 機密データを含むレスポンスには `Cache-Control: no-store` を適用する。データフロー全体で HTTPS を強制する。

### 実装チェックリスト
- 集中バリデータ：型、範囲、長さ、列挙。チェック前の正規化。
- SQL は 100% パラメータ化。動的な識別子は許可リストのみ。
- LDAP の DN／フィルタエスケープを使用。クエリ前に入力を検証。
- 信頼できない入力に対するシェル起動は行わない。やむを得ない場合は構造化 exec + 許可リスト + 正規表現検証。
- JS オブジェクトグラフの強化：安全なコンストラクタ、プロトタイプ経路のブロック、安全なマージユーティリティ。
- ファイルアップロードはコンテンツ、サイズ、拡張子で検証。Web ルート外に保存しスキャンする。

### テスト計画
- クエリ／コマンド内の文字列連結と危険な DOM／マージシンクの静的チェック。
- SQL／LDAP／OS インジェクションベクトルへのファジング。バリデータの境界ケースの単体テスト。
- ブロックされたプロトタイプキーとディープマージの挙動を検証するネガティブテスト。
