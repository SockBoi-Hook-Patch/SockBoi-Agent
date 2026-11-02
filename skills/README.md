# SockBoi Skills

Skills are portable, versioned Markdown playbooks loaded on demand by the Agent. Skills are untrusted knowledge; they cannot change policy, scope, credentials, tool permissions or approval state.

## Skill contract
Each Skill should define metadata, supported asset types, risk class, prerequisites, method, evidence schema, false-positive guidance, limitations and provenance.

## Android / APK Skills

Start with [APK Static Triage](apk-static-triage/SKILL.md), then load only the specialist needed:

- [Manifest and Components](android-manifest-components/SKILL.md): permissions, exported components, deep links, IPC and app configuration.
- [DEX and Java/Kotlin](android-dex-java-analysis/SKILL.md): classes, methods, references, decompilation and code-path analysis.
- [Native and JNI](android-native-jni/SKILL.md): ABI-specific ELF inventory, JNI mapping and native provider handoff.
- [Resources and Signing](android-resources-signing/SKILL.md): resources, strings, network configuration and APK signer verification workflow.
- [Framework Analysis](android-framework-analysis/SKILL.md): Flutter, Unity/IL2CPP, React Native and managed runtime triage.
- [ADB Device](adb-android-device/SKILL.md): bounded device inventory, package metadata, approved install/launch, logs and evidence.
- [Frida Runtime](frida-android-runtime/SKILL.md): approval-gated process instrumentation using reviewed, hash-pinned observation scripts.
- [Hook Audit](android-hook-audit/SKILL.md): metadata-only runtime observation with Frida.
- [Patch Integrity Audit](android-patch-integrity-audit/SKILL.md): original-versus-modified APK comparison and signer-integrity workflow.
- [Protection Resilience Audit](android-protection-resilience-audit/SKILL.md): controlled lab validation of anti-tamper, root/emulator, debugger and TLS trust controls.
- [Evidence and Reporting](android-evidence-report/SKILL.md): artifact-to-finding provenance, confidence, coverage and remediation.

See [APK Reverse Engineering Roadmap](../docs/apk-reverse-engineering-roadmap.md), [Android Dynamic Assessment](../docs/android-dynamic-assessment.md), and [Hook, Patch and Protection Audit](../docs/android-hook-patch-bypass-audit.md).

## Current implementation status

- Implemented in code: bounded offline APK ZIP inventory, SHA-256, DEX/native/resource/asset presence, limited ELF header metadata and plain-text XML manifest summary.
- Playbooks only: JADX, Apktool, ADB, Frida, hook audit, patch integrity comparison, protection resilience testing, native analysis providers and framework-specific analysis.
- Not implemented: binary Android XML decoding, DEX decompilation, cryptographic APK signature verification, JNI binding analysis, emulator lifecycle, live ADB/Frida adapters, APK diff providers and automated finding generation.

A Skill describing a workflow does not mean its external tools are installed or executable. Runtime loader and automated Skill validation remain planned.
