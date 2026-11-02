---
name: android-evidence-report
version: 1.0.0
description: Correlate Android static and approved dynamic observations into traceable findings and assessment reports.
allowed_asset_types: [android-apk, android-device, android-emulator]
risk_class: passive
---
# Android Evidence and Reporting

## Evidence graph
Model each case as artifact (SHA-256) → tool run → observation → finding → remediation. Each node must retain tenant and Engagement ownership, timestamps, tool/script versions, source selectors, evidence digest, coverage and limitations.

## Finding quality
- Confirmed: directly supported by reproducible evidence and validated conditions.
- Potential: credible indicator but exploitability or runtime reachability is not established.
- Informational: configuration or implementation fact without demonstrated security impact.
- False positive: contradicted by evidence; retain rationale rather than silently deleting it.

## Required report sections
1. Executive summary and target identity.
2. Authorization reference, scope, test window and exclusions.
3. Artifact integrity (SHA-256, package/version, signer observations).
4. Methodology and exact tool versions.
5. Static analysis coverage: manifest, DEX, resources, native/JNI, framework.
6. Dynamic analysis coverage: device fingerprint, approved ADB/Frida operations, script digests, scenarios and event limits.
7. Findings with severity, impact, evidence, reproducibility and remediation.
8. False positives, unknowns, unavailable tools and untested paths.
9. Cleanup, data retention and retest plan.

## Evidence hygiene
Redact secrets and personal data before persistence. Never place raw credentials, session tokens, private keys or customer data in report attachments. Hashes establish integrity, not correctness. Tool output and decompiler pseudocode are untrusted observations, not ground truth.

## Safety
Never promote a static indicator into a confirmed exploit without validation. Never claim runtime coverage when no device test ran.
