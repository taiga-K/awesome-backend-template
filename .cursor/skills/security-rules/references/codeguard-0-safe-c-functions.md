# C/C++ で安全なメモリ・文字列関数を優先する

- `rule_id`: `codeguard-0-safe-c-functions`
- 原題: Prioritize Safe Memory and String Functions in C/C++

C または C++ のコードを扱う際、主な指針はメモリ安全性の確保である。コードベースで見つかった安全でない関数を積極的に特定し、フラグを立て、安全なリファクタリング案を示すこと。新規コードを生成する際は、常にそのタスクに対して可能な限り安全な関数を既定とすること。

### 1. 避けるべき不安全な関数と安全な代替

「不安全」に挙げた関数は非推奨かつ高リスクとして扱うこと。常に下記の「推奨される安全な代替」のいずれかへの置き換えを勧めること。

• `gets()` は決して使わない — 重大なセキュリティリスクである。境界チェックが一切なく、古典的なバッファオーバーフローの原因になる。常に `fgets(char *str, int n, FILE *stream)` に置き換えること。

• `strcpy()` は避ける — 境界をチェックしない高リスク関数である。ヌル終端までコピーするため、宛先バッファを簡単に超えて書き込める。`snprintf()`、`strncpy()`（ただし注意が必要）、または `strcpy_s()`（C11 Annex K 対応時）を使うこと。

• `strcat()` は使わない — 境界チェックのない別の高リスク関数。文字列に追記し、割り当てメモリを容易に超えて書き込める。`snprintf()`、`strncat()`（慎重に扱う）、または `strcat_s()`（C11 Annex K）に置き換えること。

• `sprintf()` と `vsprintf()` を置き換える — 出力バッファの境界をチェックしない高リスク。整形後の文字列がバッファより大きいとバッファオーバーフローになる。代わりに `snprintf()`、`snwprintf()`、または `vsprintf_s()`（C11 Annex K）を使うこと。

• `scanf()` 系は注意 — 中程度のリスク。幅指定のない `%s` はバッファオーバーフローを引き起こしうる。次を行うこと:
  1. `scanf("%127s", buffer)` のように幅指定を使う
  2. さらに良い方法: `fgets()` で行を読み、`sscanf()` で解析する

• `strtok()` は避ける — 中程度のリスク。再入可能ではなく、スレッドセーフでもなく、静的な内部バッファを使うため、マルチスレッドや複雑なシグナル処理で予測不能な挙動になりうる。代わりに `strtok_r()`（POSIX）または `strtok_s()`（C11 Annex K）を使うこと。

• `memcpy()` と `memmove()` は慎重に — 本質的に不安全ではないが、サイズ引数の誤算や検証不足でバグのよくある原因になる。次を行うこと:
  1. サイズ計算を二重に確認する
  2. 利用可能なら `memcpy_s()`（C11 Annex K）を優先する
  3. コピー元とコピー先が重なる可能性がある場合は `memmove()` を使う

### 2. 実行可能な実装ガイドライン

#### 新規コード生成向け:

- `gets()`、`strcpy()`、`strcat()`、`sprintf()` を使うコードは生成しないこと。

- 文字列の整形・連結には既定で `snprintf()` を使うこと。多くの場合、最も柔軟で安全な選択肢である。

- ファイルや標準入力からの文字列入力の読み取りには既定で `fgets()` を使うこと。

#### コード分析・リファクタリング向け:

1. 特定: コードを走査し、「不安全」列の関数のすべての箇所にフラグを立てる。

2. リスクの説明: 不安全な関数にフラグを立てたとき、その脆弱性について簡潔に説明する。

    - _説明の例:_ `警告: 'strcpy' 関数は境界チェックを行わず、ソース文字列が宛先バッファより長い場合にバッファオーバーフローを引き起こしうる。よくあるセキュリティ上の脆弱性である。`

3. 文脈に応じた置換: 提案は、周辺コードの文脈を踏まえた、そのまま差し替え可能で安全な代替でなければならない。

#### コンパイラフラグ:

コンパイル時および実行時にバッファオーバーフローを検出するため、次の保護用コンパイラフラグを有効にすること:

- スタック保護: `-fstack-protector-all` または `-fstack-protector-strong` でスタック上のバッファオーバーフローを検出
- アドレスサニタイザ: 開発時に `-fsanitize=address` でメモリエラーを捕捉
- オブジェクトサイズチェック（OSC）: `-D_FORTIFY_SOURCE=2` で `strcpy`、`strcat`、`sprintf` などの多くの不安全関数に対する実行時境界チェックを有効化
- 書式文字列保護: `-Wformat -Wformat-security` で書式文字列の脆弱性を検出

### 3. リファクタリング例

提案は具体的で実行可能であること。

例 1: `strcpy` の置換

- 元の不安全なコード:

    ```
    char destination[64];
    strcpy(destination, source_string);
    ```

- 推奨するリファクタリング:

    ```
    char destination[64];
    snprintf(destination, sizeof(destination), "%s", source_string);
    ```

- 説明: `'strcpy' を 'snprintf' に置き換え、宛先バッファに書き込むのは最大 63 文字とヌル終端までにし、潜在的なバッファオーバーフローを防ぐ。`


例 2: `strncpy` 使用の是正

`strncpy` はよくあるが完璧ではない代替である。宛先バッファがヌル終端されない場合がある。使う必要がある、または使われている場合は、正しい扱いを強制すること。

- 元の（潜在的に不安全な）`strncpy`:

    ```
    // strlen(source) >= 10 のとき不安全
    char dest[10];
    strncpy(dest, source, sizeof(dest));
    ```

- 是正した提案:

    ```
    char dest[10];
    strncpy(dest, source, sizeof(dest) - 1);
    dest[sizeof(dest) - 1] = '\0';
    ```

- 説明: `'strncpy' に明示的なヌル終端を追加した。'strncpy' はソースが宛先バッファと同じ長さの場合、ヌル終端された文字列を保証しない。この修正により、後続の文字列操作でバッファ外読み取りのリスクを防ぐ。`


例 3: `scanf` の安全化

- 元の不安全なコード:

    ```
    char user_name[32];
    printf("Enter your name: ");
    scanf("%s", user_name);
    ```

- 推奨するリファクタリング:

    ```
    char user_name[32];
    printf("Enter your name: ");
    if (fgets(user_name, sizeof(user_name), stdin)) {
        // 任意: fgets の末尾改行を除去
        user_name[strcspn(user_name, "\n")] = 0;
    }
    ```

- 説明: `'scanf("%s", ...)' を 'fgets()' に置き換えてユーザー入力を読み取る。'fgets' は入力をバッファサイズに制限するためより安全で、バッファオーバーフローを防ぐ。元の 'scanf' にはその保護がなかった。`


### メモリおよび文字列の安全ガイドライン

#### 不安全なメモリ関数 — 禁止

入力パラメータの境界をチェックしない次の不安全なメモリ関数は使用禁止とする:

##### 禁止するメモリ関数:
- `memcpy()` → `memcpy_s()` を使う
- `memset()` → `memset_s()` を使う
- `memmove()` → `memmove_s()` を使う
- `memcmp()` → `memcmp_s()` を使う
- `bzero()` → `memset_s()` を使う
- `memzero()` → `memset_s()` を使う

##### 安全なメモリ関数への置き換え:
```c
// 代わりに: memcpy(dest, src, count);
errno_t result = memcpy_s(dest, dest_size, src, count);
if (result != 0) {
// エラー処理
}

// 代わりに: memset(dest, value, count);
errno_t result = memset_s(dest, dest_size, value, count);

// 代わりに: memmove(dest, src, count);
errno_t result = memmove_s(dest, dest_size, src, count);

// 代わりに: memcmp(s1, s2, count);
int indicator;
errno_t result = memcmp_s(s1, s1max, s2, s2max, count, &indicator);
if (result == 0) {
// indicator に比較結果: <0, 0, または >0
}
```

#### 不安全な文字列関数 — 禁止

バッファオーバーフローを引き起こしうる次の不安全な文字列関数は使用禁止とする:

##### 禁止する文字列関数:
- `strstr()` → `strstr_s()`
- `strtok()` → `strtok_s()`
- `strcpy()` → `strcpy_s()`
- `strcmp()` → `strcmp_s()`
- `strlen()` → `strnlen_s()`
- `strcat()` → `strcat_s()`
- `sprintf()` → `snprintf()`

##### 安全な文字列関数への置き換え:
```c
// 文字列検索
errno_t strstr_s(char *dest, rsize_t dmax, const char *src, rsize_t slen, char **substring);

// 文字列トークン化
char *strtok_s(char *dest, rsize_t *dmax, const char *src, char **ptr);

// 文字列コピー
errno_t strcpy_s(char *dest, rsize_t dmax, const char *src);

// 文字列比較
errno_t strcmp_s(const char *dest, rsize_t dmax, const char *src, int *indicator);

// 文字列長（境界付き）
rsize_t strnlen_s(const char *str, rsize_t strsz);

// 文字列連結
errno_t strcat_s(char *dest, rsize_t dmax, const char *src);

// 整形文字列（常にサイズ境界付き版を使用）
int snprintf(char *s, size_t n, const char *format, ...);
```

#### 実装例:

##### 安全な文字列コピーのパターン:
```c
// 悪い例 — 不安全
char dest[256];
strcpy(dest, src); // バッファオーバーフローのリスク!

// 良い例 — 安全
char dest[256];
errno_t result = strcpy_s(dest, sizeof(dest), src);
if (result != 0) {
// エラー処理: src が長すぎる、またはパラメータが不正
EWLC_LOG_ERROR("String copy failed: %d", result);
return ERROR;
}
```

##### 安全な文字列連結のパターン:
```c
// 悪い例 — 不安全
char buffer[256] = "prefix_";
strcat(buffer, suffix); // バッファオーバーフローのリスク!

// 良い例 — 安全
char buffer[256] = "prefix_";
errno_t result = strcat_s(buffer, sizeof(buffer), suffix);
if (result != 0) {
EWLC_LOG_ERROR("String concatenation failed: %d", result);
return ERROR;
}
```

##### 安全なメモリコピーのパターン:
```c
// 悪い例 — 不安全
memcpy(dest, src, size); // 境界チェックなし!

// 良い例 — 安全
errno_t result = memcpy_s(dest, dest_max_size, src, size);
if (result != 0) {
EWLC_LOG_ERROR("Memory copy failed: %d", result);
return ERROR;
}
```

##### 安全な文字列トークン化のパターン:
```c
// 悪い例 — 不安全
char *token = strtok(str, delim); // 元の文字列を不安全に変更

// 良い例 — 安全
char *next_token = NULL;
rsize_t str_max = strnlen_s(str, MAX_STRING_SIZE);
char *token = strtok_s(str, &str_max, delim, &next_token);
while (token != NULL) {
// トークンを処理
token = strtok_s(NULL, &str_max, delim, &next_token);
}
```

#### メモリおよび文字列の安全に関するコードレビュー・チェックリスト:

##### コードレビュー前（開発者）:
- [ ] 不安全なメモリ関数（`memcpy`、`memset`、`memmove`、`memcmp`、`bzero`）を使っていない
- [ ] 不安全な文字列関数（`strcpy`、`strcat`、`strcmp`、`strlen`、`sprintf`、`strstr`、`strtok`）を使っていない
- [ ] すべてのメモリ操作が適切なサイズ引数付きの `*_s()` 系を使っている
- [ ] バッファサイズが `sizeof()` または既知の上限で正しく計算されている
- [ ] 変更されうるハードコードされたバッファサイズがない

##### コードレビュー（レビュアー）:
- [ ] メモリ安全性: すべてのメモリ操作が安全なバリアントを使っていることを確認
- [ ] バッファ境界: 宛先バッファのサイズが適切に指定されていることを確認
- [ ] エラー処理: すべての `errno_t` 戻り値が処理されていることを確認
- [ ] サイズ引数: `rsize_t dmax` パラメータが正しいことを検証
- [ ] 文字列終端: 文字列が適切にヌル終端されていることを確認
- [ ] 長さ検証: 操作前にソース文字列の長さが検証されていることを確認

##### 静的解析の統合:
- [ ] 不安全な関数使用に対するコンパイラ警告を有効にする
- [ ] 静的解析ツールで不安全な関数呼び出しを検出する
- [ ] ビルドシステムで不安全な関数の警告をエラーとして扱う
- [ ] 禁止関数をスキャンする pre-commit フックを追加する

#### よくある落とし穴と対策:

##### 落とし穴 1: サイズ引数の誤り
```c
// 誤り — 宛先サイズではなくソースサイズを使っている
strcpy_s(dest, strlen(src), src); // 誤り!

// 正しい — 宛先バッファのサイズを使う
strcpy_s(dest, sizeof(dest), src); // 正しい
```

##### 落とし穴 2: 戻り値の無視
```c
// 誤り — エラーを無視
strcpy_s(dest, sizeof(dest), src); // エラーをチェックしていない

// 正しい — 戻り値を確認
if (strcpy_s(dest, sizeof(dest), src) != 0) {
// 適切にエラー処理
}
```

##### 落とし穴 3: ポインタに対する sizeof の誤用
```c
// 誤り — バッファではなくポインタの sizeof
void func(char *buffer) {
strcpy_s(buffer, sizeof(buffer), src); // sizeof(char*) = 8 など!
}

// 正しい — バッファサイズを引数で渡す
void func(char *buffer, size_t buffer_size) {
strcpy_s(buffer, buffer_size, src);
}
```

このルールをどのように適用したか、なぜ適用したかを常に説明すること。
