---
name: android-patch-audit
version: 1.0.0
description: Compare original and modified APK builds and produce a provenance-linked, read-only patch audit.
allowed_asset_types: [android-apk]
risk_class: passive
---

# Android APK Patch Audit

## Purpose

This Skill audits changes between an original APK and a candidate patched build. It is a forensic comparison workflow, not a patcher. It does not modify APKs, repackage them, resign them, install them, or execute their code.

## Required inputs

- Original APK and candidate patched APK supplied by the authorized owner.
- Engagement ID, tenant, authorization reference, and test scope.
- Expected package name and version/build identity when known.
- SHA-256 of each input artifact.

## Workflow

1. Preserve original files as immutable evidence in the approved artifact store.
2. Compute and record SHA-256, byte size, and acquisition metadata for both APKs.
3. Run bounded ZIP validation on both files before reading members.
4. Compare archive member paths and streamed SHA-256 values.
5. Group changes into manifest, DEX, native libraries, resources, assets, signing/build metadata, and other.
6. Flag package identity changes, added/removed DEX files, changed native libraries, permission/component changes where the manifest decoder supports them, and signing metadata changes.
7. Correlate changes with the authorized change request or patch manifest.
8. Record unexplained differences as observations; do not infer maliciousness from a changed hash alone.
9. Verify APK signatures with a dedicated trusted platform tool in a separately sandboxed provider before claiming signature validity.
10. Produce a report with original/patched digests, changed-member inventory, tool versions, coverage, and limitations.

## Interpretation

- A changed DEX hash proves bytes differ, not that a specific method was patched.
- A changed META-INF entry does not prove signature validity or invalidity.
- A package-name difference is an identity mismatch requiring analyst review.
- A missing or binary manifest means component and permission comparison is incomplete.
- A changed signer should be treated as a supply-chain/integrity observation, not automatically a vulnerability.

## Safety and evidence

Do not patch third-party apps, remove licensing or payment controls, or distribute modified builds. Do not store credentials, tokens, private keys, or personal data. Maintain chain of custody and hash every artifact and report. The patch-audit API performs read-only ZIP member comparison; it does not persist either APK.
