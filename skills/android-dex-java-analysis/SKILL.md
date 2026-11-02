---
name: android-dex-java-analysis
version: 1.0.0
description: Analyze Android DEX and Java/Kotlin logic using class, method, reference and decompilation evidence.
allowed_asset_types: [android-apk]
risk_class: passive
---
# Android DEX and Java/Kotlin Analysis

## Preconditions
Bind analysis to the APK SHA-256. Record JADX/JDK/provider versions and whether the APK is multidex, obfuscated, split, or partially decoded. Use a sandboxed, pinned decompiler; no APK code is executed.

## Workflow
1. Inventory DEX files and map class descriptors to source-like names.
2. Identify app entry points, Application lifecycle, exported component handlers, deep links and IPC boundaries.
3. Search high-signal API use: WebView, networking clients, cryptography, keystore, local storage, logging, reflection, dynamic loading and JNI.
4. Select concrete classes and methods; inspect method bodies and overload identity rather than relying on name-only search.
5. Trace incoming/outgoing static references and record unresolved reflection, dynamic dispatch, native methods and missing code coverage.
6. Review authentication/session lifecycle, trust decisions, data storage, serialization and input validation as data-flow questions.
7. Correlate suspicious code paths with manifest declarations and resource configuration.
8. Record source offsets/class/method descriptors and decompiler diagnostics.

## Output
For each observation include DEX member, class/method descriptor, evidence reference, tool version, confidence, static-only caveat and recommended validation. Decompiled pseudocode is a representation, not original source or proof of runtime reachability.

## Safety
Do not extract tokens, keys, passwords or personal data into reports. Do not modify app logic or create a repackaged APK as part of this read-only Skill. Dynamic validation is routed to the separately approved ADB/Frida Skills.
