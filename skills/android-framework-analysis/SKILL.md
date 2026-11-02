---
name: android-framework-analysis
version: 1.0.0
description: Identify Flutter, Unity IL2CPP, React Native, Xamarin and other framework-specific APK layouts and route to specialist analysis.
allowed_asset_types: [android-apk]
risk_class: passive
---
# Android Framework-Specific Analysis

## Framework triage
- Flutter: inspect libflutter.so, libapp.so, asset bundles and Dart snapshot indicators; record ABI and engine/version evidence where available.
- Unity: inspect libil2cpp.so, global-metadata.dat, UnityPlayer and managed assembly indicators; correlate metadata version before selecting parsers.
- React Native: inspect Hermes/JSC runtime libraries, JS bundles, Metro/source-map artifacts and native module declarations.
- Xamarin/.NET for Android: identify managed assemblies, runtime libraries and package metadata; use a suitable managed-code analyzer.
- Other engines: preserve the observed file/class markers and route to a provider only when its format support is verified.

## Workflow
1. Identify framework from multiple independent artifact indicators.
2. Record artifact paths, digests, ABI, version evidence and conflicting signals.
3. Select a parser/decompiler with documented format/version coverage.
4. Preserve offsets, symbol/type/method identities and parser diagnostics.
5. Route JNI/native portions to android-native-jni and resources to android-resources-signing.
6. State when protection, encryption, obfuscation or missing metadata prevents reliable analysis.

## Output
Framework classification with evidence, version/format coverage, relevant files, tool requirements, analysis results and unknowns.

## Safety
Static analysis only. Do not dump runtime secrets, defeat commercial licensing, or claim complete deobfuscation. Dynamic behavior must be separately authorized.
