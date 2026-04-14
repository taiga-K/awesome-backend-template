# 暗号のセキュリティガイドラインとポスト量子への備え

- `rule_id`: `codeguard-1-crypto-algorithms`
- 原題: Cryptographic Security Guidelines & Post-Quantum Readiness

## 1. 禁止（不安全）アルゴリズム

次のアルゴリズムは破られているか、根本的に不安全として知られている。これらを含むコードを生成・使用してはならない。

*   ハッシュ: `MD2`, `MD4`, `MD5`, `SHA-0`
*   対称: `RC2`, `RC4`, `Blowfish`, `DES`, `3DES`
*   鍵交換: 静的 RSA、匿名 Diffie-Hellman
*   古典: `Vigenère`

理由: 暗号的に破られており、衝突攻撃や中間者攻撃に脆弱である。

## 2. 非推奨（レガシー/弱い）アルゴリズム

次のアルゴリズムには既知の弱点があるか、旧式とみなされる。新規設計では避け、移行を優先すること。

*   ハッシュ: `SHA-1`
*   対称: `AES-CBC`, `AES-ECB`
*   署名: `PKCS#1 v1.5` パディング付き RSA
*   鍵交換: 弱い/共通の素数を用いた DHE

## 3. 推奨およびポスト量子対応アルゴリズム

古典および量子の脅威の両方に耐性を持たせるため、これらの現代的で安全なアルゴリズムを実装すること。

### 対称暗号
*   標準: `AES-GCM`（AEAD）、（許可される場合）`ChaCha20-Poly1305`。
*   PQC 要件: AES-256 鍵（またはそれ以上）を優先する。量子攻撃（Grover のアルゴリズム）に耐性がある。
*   避けること: 独自暗号や認証のないモード。

### 鍵交換（KEM）
*   標準: ECDHE（`X25519` または `secp256r1`）
*   PQC 要件: サポートされる場合はハイブリッド鍵交換（古典 + PQC）を使う。
    *   推奨: `X25519MLKEM768`（X25519 + ML-KEM-768）
    *   代替: `SecP256r1MLKEM768`（P-256 + ML-KEM-768）
    *   高保証: `SecP384r1MLKEM1024`（P-384 + ML-KEM-1024）
*   純 PQC: ML-KEM-768（ベースライン）または ML-KEM-1024。ML-KEM-512 は明示的なリスク受容がない限り避ける。
*   制約:
    *   ベンダー文書化された識別子（RFC 9242/9370）を使う。
    *   レガシー/ドラフトの「Hybrid-Kyber」グループ（例: `X25519Kyber`）やドラフトまたはハードコードされた OID を削除する。

### 署名と証明書
*   標準: ECDSA（`P-256`）
*   PQC 移行: ハードウェア支援（HSM/TPM）の ML-DSA が利用可能になるまで、mTLS とコード署名には引き続き ECDSA（`P-256`）を使う。
*   ハードウェア要件: ソフトウェアのみの鍵で PQC ML-DSA 署名を有効にしない。HSM/TPM 保管を必須とする。

### プロトコルバージョン
*   (D)TLS: (D)TLS 1.3 のみ（またはそれ以降）を強制する。
*   IPsec: IKEv2 のみを強制する。
    *   AEAD 付き ESP（AES-256-GCM）を使う。
    *   ECDHE による PFS を必須とする。
    *   ハイブリッド PQC（ML-KEM + ECDHE）には RFC 9242 および RFC 9370 を実装する。
    *   再鍵（CREATE_CHILD_SA）でハイブリッドアルゴリズムが維持されることを確認する。
*   SSH: ベンダーがサポートする PQC/ハイブリッド KEX のみを有効にする（例: `sntrup761x25519`）。

## 4. 安全な実装ガイドライン

### 一般的なベストプラクティス
*   設定による制御: アルゴリズム選択を設定/ポリシーで公開し、コード変更なしで切り替え可能にする。
*   鍵管理:
    *   鍵保管には KMS/HSM を使う。
    *   CSPRNG で鍵を生成する。
    *   暗号化鍵と署名鍵を分離する。
    *   ポリシーに従い鍵をローテーションする。
    *   鍵、秘密、実験用 OID をハードコードしてはならない。
*   テレメトリ: PQC 採用状況を監視するため、交渉されたグループ、ハンドシェイクサイズ、失敗原因を記録する。

### 非推奨 SSL/暗号 API（C/OpenSSL）— 禁止

次の非推奨関数は使用してはならない。代わりに高レベル EVP API を使うこと。

#### 対称暗号（AES）
- 非推奨: `AES_encrypt()`, `AES_decrypt()`
- 置き換え:

  EVP_EncryptInit_ex()   // PQC 対応のため EVP_aes_256_gcm() を使用
  EVP_EncryptUpdate()
  EVP_EncryptFinal_ex()


#### RSA / PKEY 操作
- 非推奨: `RSA_new()`, `RSA_free()`, `RSA_get0_n()`
- 置き換え:

  EVP_PKEY_new()
  EVP_PKEY_up_ref()
  EVP_PKEY_free()
 

#### ハッシュと MAC 関数
- 非推奨: `SHA1_Init()`, `HMAC()`（特に SHA1 との組み合わせ）
- 置き換え:

  EVP_DigestInit_ex() // SHA-256 以上を使用
  EVP_Q_MAC()         // ワンショット MAC 用


## 5. Broccoli プロジェクト固有の要件
- SHA1 付き HMAC(): 非推奨。
- 置き換え: SHA-256 以上の HMAC を使用する。

HMAC-SHA1 の安全な置き換えの例:

```c
EVP_Q_MAC(NULL, "HMAC", NULL, "SHA256", NULL, key, key_len, data, data_len, out, out_size, &out_len);
```

## 6. 安全な暗号実装パターン

安全な AES-256-GCM 暗号化の例（PQC 対応の対称強度）:

```c
EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
if (!ctx) handle_error();

// AES-256-GCM を使用
if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, key, iv) != 1)
    handle_error();

int len, ciphertext_len;
if (EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len) != 1)
    handle_error();
ciphertext_len = len;

if (EVP_EncryptFinal_ex(ctx, ciphertext + len, &len) != 1)
    handle_error();
ciphertext_len += len;

EVP_CIPHER_CTX_free(ctx);
```
