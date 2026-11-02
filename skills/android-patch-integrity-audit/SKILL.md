---
name: android-patch-integrity-audit
version: 1.0.0
description: Compare authorized original and modified APK artifacts, explain binary changes, and verify package/signature integrity without modifying or resigning apps.
allowed_asset_types: [android-apk, android-apk-pair]
risk_class: medium
requires_human_approval: [artifact.compare, signer.verify]
---

# Android Patch Integrity Audit Skill

## Objective

Audit a user-supplied original APK and a separately supplied patched/rebuilt APK. Identify what changed, whether changes match the approved change request, and whether package identity and signing properties remain valid.

This Skill does not patch, repackage, resign, remove licensing, alter payment logic, or bypass app protections. It analyzes artifacts supplied by an authorized owner.

**Implementation status:** Playbook only. APK diff providers, DEX decompilation, resource decoding and cryptographic signer verification are not yet implemented in the application.

## Required artifacts

- Original APK and modified APK, each independently uploaded through the tenant-scoped artifact intake.
- SHA-256 and byte size for both files.
- Engagement authorization and approved change request.
- Expected package name, version policy and signer certificate fingerprints.
- Build provenance, toolchain versions and patch author where available.

Reject ambiguous artifact roles, mismatched tenant/Engagement, unsafe archives, and files that exceed configured limits.

## Comparison workflow

1. Hash both APKs and preserve immutable artifact identities.
2. Compare ZIP entry inventories: added, removed, renamed and changed members.
3. Compare AndroidManifest fields: package, version, SDK levels, permissions, exported components, intent filters, debuggable, backup and cleartext settings.
4. Compare DEX inventory and, when a sandboxed decompiler is available, class/method-level changes.
5. Compare native libraries by ABI and ELF metadata; use a dedicated static provider for deeper symbol/section comparison.
6. Compare resources, assets and network security configuration.
7. Verify APK signatures and signer certificate fingerprints with a trusted Android platform tool. Do not infer validity from META-INF files alone.
8. Compare the observed changes against the approved change request.
9. Generate a change report with unexplained deltas and coverage gaps.

## Change classification

- expected: explicitly listed and justified in the change request.
- security-relevant: permission/component/network/trust/security-control changes.
- unexplained: changed but not mapped to an approved change.
- integrity-failure: malformed artifact, invalid signature, unexpected signer or package identity mismatch.
- unknown: the required decoder/provider is unavailable.

A binary difference is not automatically malicious. A missing decoder must result in an unknown status, not a guessed conclusion.

## Guardrails

- Never execute either APK as part of this Skill.
- Never modify or overwrite source artifacts.
- Never generate a patched APK or signing key.
- Never treat a successful upload as proof of signature validity.
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
  "signer_fingerprint_match": null,
  "added_entries": [],
  "removed_entries": [],
  "changed_entries": [],
  "security_relevant_changes": [],
  "unexplained_changes": [],
  "provider_versions": [],
  "coverage_limitations": []
}
~~~

## Acceptance tests

- Reject cross-tenant artifact references and swapped artifact roles.
- Preserve both input hashes in all derived evidence.
- Test ZIP inventory edge cases and duplicate/path traversal handling.
- Verify signer mismatch is reported as failure only when a real verifier ran.
- Verify missing decompiler/signature provider yields unknown rather than pass.
- Confirm no output APK is created or source artifact changed.
