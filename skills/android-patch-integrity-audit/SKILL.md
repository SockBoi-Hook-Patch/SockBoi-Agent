---
name: android-patch-integrity-audit
version: 1.1.0
description: Compare authorized original and modified APK artifacts, explain binary changes, and report signer verification as unknown until a trusted verifier is integrated.
allowed_asset_types: [android-apk, android-apk-pair]
risk_class: medium
requires_human_approval: [artifact.compare, signer.verify]
---

# Android Patch Integrity Audit Skill

## Objective

Audit a user-supplied original APK and a separately supplied patched/rebuilt APK. Identify what changed, whether changes match the approved change request, and whether package identity and signing properties remain valid.

This Skill does not patch, repackage, resign, remove licensing, alter payment logic, or bypass app protections. It analyzes artifacts supplied by an authorized owner.

**Implementation status:** Offline ZIP-member comparison is implemented in `sockboi.apk_patch_audit.compare_apk_bytes` and exposed by `POST /engagements/{engagement_id}/apk/compare`. DEX decompilation, resource decoding, semantic code diff and cryptographic signer verification are not implemented.

## Required artifacts

- Original APK and modified APK, each submitted in the tenant-scoped comparison request.
- SHA-256 and byte size for both files.
- Engagement authorization and approved change request.
- Expected package name, version policy and signer certificate fingerprints.
- Build provenance, toolchain versions and patch author where available.

Reject ambiguous artifact roles, mismatched tenant/Engagement, unsafe archives, and files that exceed configured limits.

## Comparison workflow

1. Hash both APKs and preserve immutable artifact identities.
2. Validate both ZIP containers using the bounded APK inspector.
3. Compare ZIP entry inventories: added, removed and changed members; identify member changes by SHA-256.
4. Compare package identity when both manifests are parseable as plain XML. Binary Android XML remains unknown until a decoder is integrated.
5. Flag changes to manifest, DEX, native libraries, signing metadata and network-security resources as security-relevant for review.
6. Use a sandboxed decompiler/resource provider for class/method and semantic resource changes when available.
7. Verify APK signatures and signer certificate fingerprints with a trusted Android platform tool. Do not infer validity from META-INF files alone.
8. Compare observed changes against the approved change request.
9. Generate a change report with unexplained deltas and coverage gaps.

## Change classification

- expected: explicitly listed and justified in the change request.
- security-relevant: permission/component/network/trust/security-control changes.
- unexplained: changed but not mapped to an approved change.
- integrity-failure: malformed artifact or package identity mismatch; signer failure only when a real verifier ran.
- unknown: required decoder/provider is unavailable or signer verification has not run.

A binary difference is not automatically malicious. A missing decoder must result in an unknown status, not a guessed conclusion.

## Guardrails

- Never execute either APK as part of this Skill.
- Never modify or overwrite source artifacts.
- Never generate a patched APK or signing key.
- Never treat a successful upload or presence of META-INF files as proof of signature validity.
- Keep original and modified artifacts tenant-isolated and access-controlled.
- Redact secrets accidentally present in build metadata or resources.

## Evidence schema

~~~json
{
  "evidence_type": "android.apk.patch_comparison",
  "engagement_id": "…",
  "original_sha256": "…",
  "modified_sha256": "…",
  "package_identity_match": null,
  "manifest_changed": false,
  "added_entries": [],
  "removed_entries": [],
  "changed_entries": [],
  "security_relevant_changes": [],
  "signer_comparison": {"status": "not_verified"},
  "execution_performed": false,
  "source_artifacts_modified": false,
  "output_apk_created": false,
  "coverage_limitations": []
}
~~~

## Acceptance tests

- Reject cross-tenant artifact access and swapped artifact roles.
- Preserve both input hashes in all derived evidence.
- Test ZIP inventory edge cases, duplicate paths, traversal and compression limits.
- Verify package mismatch is reported when parseable; binary manifests yield unknown.
- Verify signer status remains not_verified until a real verifier runs.
- Confirm no output APK is created or source artifact changed.
