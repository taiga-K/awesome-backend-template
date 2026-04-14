---
name: security-rules
description: Provides CodeGuard-based security rules for design, implementation, and code review in this repo. Use when reviewing security, hardening code, or assessing authentication, authorization, input validation, secrets, logging, APIs, TLS, containers, CI/CD, IaC, supply chain, MCP, or mobile security.
---

# セキュリティルール

## いつ使うか

- セキュリティ観点で設計、実装、コードレビューを行うとき
- `codeguard-*` ルールの意図や期待される安全策を日本語で確認したいとき
- 認証、認可、入力検証、秘密情報、ログ、API、TLS、IaC、CI/CD、コンテナ、モバイル、MCP など個別領域の安全策を参照したいとき

## 使い方

1. 対象領域に対応する `rule_id` を選ぶ
2. 対応する `references/*.md` を読む
3. 実装やレビューでは、本文だけでなくチェックリストやテスト計画まで反映する
4. レビューでは、該当する `rule_id` を根拠として指摘や判断に反映する
5. 判定や説明では、該当する `references/*.md` を正本として参照する

## 領域別の入口

- 認証・MFA: `codeguard-0-authentication-mfa`
- 認可・アクセス制御: `codeguard-0-authorization-access-control`
- セッション・Cookie: `codeguard-0-session-management-and-cookies`
- 入力検証・インジェクション: `codeguard-0-input-validation-injection`
- API・Web サービス: `codeguard-0-api-web-services`
- ログ・監査: `codeguard-0-logging`
- 秘密情報・証明書・暗号: `codeguard-1-hardcoded-credentials` / `codeguard-1-digital-certificates` / `codeguard-1-crypto-algorithms` / `codeguard-0-additional-cryptography`
- データ保護・保存: `codeguard-0-data-storage` / `codeguard-0-privacy-data-protection`
- ファイル処理・アップロード: `codeguard-0-file-handling-and-uploads`
- XML・デシリアライゼーション: `codeguard-0-xml-and-serialization`
- IaC・Kubernetes・CI/CD・サプライチェーン: `codeguard-0-iac-security` / `codeguard-0-cloud-orchestration-kubernetes` / `codeguard-0-devops-ci-cd-containers` / `codeguard-0-supply-chain-security`
- クライアント・モバイル・MCP: `codeguard-0-client-side-web-security` / `codeguard-0-mobile-apps` / `codeguard-0-mcp-security`
- 言語・フレームワーク・C 系安全関数: `codeguard-0-framework-and-languages` / `codeguard-0-safe-c-functions`

## 対応リファレンス

- `codeguard-0-additional-cryptography`: [references/codeguard-0-additional-cryptography.md](references/codeguard-0-additional-cryptography.md)
- `codeguard-0-api-web-services`: [references/codeguard-0-api-web-services.md](references/codeguard-0-api-web-services.md)
- `codeguard-0-authentication-mfa`: [references/codeguard-0-authentication-mfa.md](references/codeguard-0-authentication-mfa.md)
- `codeguard-0-authorization-access-control`: [references/codeguard-0-authorization-access-control.md](references/codeguard-0-authorization-access-control.md)
- `codeguard-0-client-side-web-security`: [references/codeguard-0-client-side-web-security.md](references/codeguard-0-client-side-web-security.md)
- `codeguard-0-cloud-orchestration-kubernetes`: [references/codeguard-0-cloud-orchestration-kubernetes.md](references/codeguard-0-cloud-orchestration-kubernetes.md)
- `codeguard-0-data-storage`: [references/codeguard-0-data-storage.md](references/codeguard-0-data-storage.md)
- `codeguard-0-devops-ci-cd-containers`: [references/codeguard-0-devops-ci-cd-containers.md](references/codeguard-0-devops-ci-cd-containers.md)
- `codeguard-0-file-handling-and-uploads`: [references/codeguard-0-file-handling-and-uploads.md](references/codeguard-0-file-handling-and-uploads.md)
- `codeguard-0-framework-and-languages`: [references/codeguard-0-framework-and-languages.md](references/codeguard-0-framework-and-languages.md)
- `codeguard-0-iac-security`: [references/codeguard-0-iac-security.md](references/codeguard-0-iac-security.md)
- `codeguard-0-input-validation-injection`: [references/codeguard-0-input-validation-injection.md](references/codeguard-0-input-validation-injection.md)
- `codeguard-0-logging`: [references/codeguard-0-logging.md](references/codeguard-0-logging.md)
- `codeguard-0-mcp-security`: [references/codeguard-0-mcp-security.md](references/codeguard-0-mcp-security.md)
- `codeguard-0-mobile-apps`: [references/codeguard-0-mobile-apps.md](references/codeguard-0-mobile-apps.md)
- `codeguard-0-privacy-data-protection`: [references/codeguard-0-privacy-data-protection.md](references/codeguard-0-privacy-data-protection.md)
- `codeguard-0-safe-c-functions`: [references/codeguard-0-safe-c-functions.md](references/codeguard-0-safe-c-functions.md)
- `codeguard-0-session-management-and-cookies`: [references/codeguard-0-session-management-and-cookies.md](references/codeguard-0-session-management-and-cookies.md)
- `codeguard-0-supply-chain-security`: [references/codeguard-0-supply-chain-security.md](references/codeguard-0-supply-chain-security.md)
- `codeguard-0-xml-and-serialization`: [references/codeguard-0-xml-and-serialization.md](references/codeguard-0-xml-and-serialization.md)
- `codeguard-1-crypto-algorithms`: [references/codeguard-1-crypto-algorithms.md](references/codeguard-1-crypto-algorithms.md)
- `codeguard-1-digital-certificates`: [references/codeguard-1-digital-certificates.md](references/codeguard-1-digital-certificates.md)
- `codeguard-1-hardcoded-credentials`: [references/codeguard-1-hardcoded-credentials.md](references/codeguard-1-hardcoded-credentials.md)

## 注意

- `references/*.md` がこのスキルで参照する正本である
- 関連するルールだけを開いて判断し、無関係な領域まで広げすぎない
- 実装時は対策とチェックリストを反映し、レビュー時は不足や逸脱の有無を確認する
