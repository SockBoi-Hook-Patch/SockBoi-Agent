---
name: android-native-jni
version: 1.0.0
description: Inventory Android native libraries and correlate JNI declarations with ABI-specific ELF evidence.
allowed_asset_types: [android-apk]
risk_class: passive
---
# Android Native and JNI Analysis

## Workflow
1. Inventory lib/<abi>/*.so and record SHA-256, size, ELF class, endianness, machine, build-id and available symbols.
2. Identify APK ABI coverage and compare with device ABI only when supplied by an approved device inventory.
3. Extract DEX native method declarations and correlate JNI names/signatures with candidate exports and registration tables.
4. Distinguish statically named JNI exports from RegisterNatives-based dynamic registration; report unresolved candidates and partial scans.
5. Inspect imports, exports, relocations, strings, security-relevant API references and call relationships using a pinned native analysis provider.
6. For Unity IL2CPP, route global-metadata.dat and libil2cpp.so to the framework specialist; do not treat guessed offsets as verified.
7. Preserve provider version, analysis database identity, function address/RVA, ABI, file digest and scan coverage.

## Toolchain
Use Ghidra, Rizin/radare2, or a properly licensed IDA/JEB installation supplied by the operator. Do not install cracked tools or download arbitrary native plugins. Tool bootstrap must be pinned and approved.

## Output
Produce an ABI/library matrix, JNI declaration-to-candidate mapping, function evidence, unresolved rows, provider limitations and next-analysis recommendations.

## Safety
This Skill is static and read-only. Do not inject libraries, patch native code, dump process memory, or attach to unrelated processes. Runtime observation requires the Frida Skill and an approved disposable emulator.
