---
name: android-manifest-components
version: 1.0.0
description: Analyze Android manifest declarations, permissions, exported components, deep links, IPC boundaries and app configuration.
allowed_asset_types: [android-apk]
risk_class: passive
---
# Android Manifest and Component Review

## Inputs
Require APK SHA-256, decoded manifest provenance, package identity, Android target/min SDK when available, and Engagement reference. Binary manifest output must come from a pinned decoder; never guess from raw binary XML.

## Review sequence
1. Confirm package identity and decoder/tool version.
2. Inventory requested permissions and compare them with observed app features.
3. Review application flags: debuggable, allowBackup, usesCleartextTraffic, networkSecurityConfig, extractNativeLibs and task/backup configuration.
4. Inventory activities, aliases, services, receivers and providers. Record exported state, permission guards, process, authorities and intent filters.
5. Review custom schemes, app links, verified links, host/path constraints and authentication state assumptions.
6. Trace IPC entry points to authorization checks and sensitive operations using static references and approved test evidence.
7. Flag implicit exported behavior when target SDK semantics make the effective value relevant; preserve uncertainty if decoder data is incomplete.

## Output
Produce a component matrix with component type/name, exported status (explicit/inferred/unknown), permission, intent filters, externally reachable inputs, downstream sensitive operation, evidence location, severity rationale and remediation.

## Safety
Do not invoke exported components or send crafted intents from this static Skill. Dynamic validation requires a separately scoped ADB action and human approval. Avoid collecting personal data or calling remote deep links outside scope.
