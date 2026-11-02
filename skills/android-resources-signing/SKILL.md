---
name: android-resources-signing
version: 1.0.0
description: Inspect Android resources, localized strings, network configuration, APK signing metadata and build provenance.
allowed_asset_types: [android-apk, android-app-bundle, android-split-apk]
risk_class: passive
---
# Android Resources and APK Signing Review

## Resource workflow
1. Decode resources with a pinned Apktool/aapt2 version in an isolated worker.
2. Inventory strings, locales, layouts, XML resources, assets and resource references.
3. Review network security configuration, cleartext policy, trust-anchor declarations, backup rules, file-provider paths and deep-link declarations.
4. Identify embedded endpoints, feature flags and SDK/configuration artifacts; redact credentials and personal data.
5. Record missing resources, decode failures and split-APK dependencies.

## Signing workflow
1. Record the original artifact digest and all APK/split identities.
2. Inspect signer certificates, certificate fingerprints, signing schemes and lineage with a trusted verifier.
3. Distinguish signer inventory from cryptographic verification. META-INF certificate files alone do not establish APK signature validity.
4. Compare signer identity and build metadata only against an operator-supplied trusted baseline.
5. Report debug/test certificates, signer changes, inconsistent split signatures or unverifiable provenance as evidence-led observations.

## Output
Resource inventory, locale coverage, configuration observations, signer/certificate fingerprints, verifier/tool versions, verification result, and limitations.

## Safety
Do not modify, resign or distribute an APK in this Skill. Repackaging and installation are separate state-changing operations requiring explicit authorization and approval.
