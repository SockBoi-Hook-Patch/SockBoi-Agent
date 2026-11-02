---
name: android-protection-resilience-audit
version: 1.0.0
description: Assess Android app anti-tamper, root/emulator, debugger and TLS trust controls using authorized lab scenarios and observation-only instrumentation.
allowed_asset_types: [android-apk, android-emulator, android-device]
risk_class: high
requires_human_approval: [frida.attach, frida.script.load_reviewed, android.test_case.run]
---

# Android Protection Resilience Audit Skill

## Objective

Determine whether an app's security controls detect and respond appropriately to controlled test conditions in a lab. This is a resilience assessment, not an instruction set for defeating protections in third-party apps.

**Implementation status:** Playbook only. No automated bypass engine, device lab, or live Frida adapter is implemented.

## Controls in scope

- Root / privileged-environment detection.
- Emulator / virtual-device detection.
- Debugger and instrumentation detection.
- APK integrity and signer validation.
- TLS certificate validation and certificate pinning behavior.
- Runtime integrity and tamper response.
- Sensitive-data handling when a control reports failure.

## Test model

Use an explicitly authorized test build or purpose-built lab APK with documented expected behavior. Prefer vendor-provided debug/test toggles or controlled emulator configurations. Do not attempt to evade or disable a production app's controls.

For each control, define:
- control owner and security objective;
- baseline environment and expected result;
- controlled lab condition and expected result;
- app response (block, warn, degrade safely, or continue);
- evidence sources and data minimization;
- residual risk and known false positives.

## Assessment procedure

1. Confirm the Engagement specifically authorizes control-resilience testing.
2. Verify package, APK digest, signer and assigned disposable emulator.
3. Establish a clean baseline and record Android build/device metadata.
4. Run the approved baseline test case and record app-reported control outcomes.
5. Run only the documented lab test variants, such as emulator configurations or a vendor-supplied test build.
6. Use reviewed observation hooks to record whether the control was invoked and what result the app reported; do not change method arguments or return values.
7. Record whether the app's response matches its documented security policy.
8. Repeat tests to identify flaky detections and false positives.
9. Clean the emulator and produce evidence-backed findings.

## Reporting semantics

Use only these outcomes:
- **effective in tested conditions:** observed behavior matched the documented expectation for every executed test.
- **ineffective in tested conditions:** a controlled test demonstrated a specific policy failure.
- **inconsistent:** repeated runs produced conflicting outcomes.
- **not tested:** no approved fixture or test condition was available.
- **inconclusive:** instrumentation, environment, or coverage limitations prevent a reliable conclusion.

Do not claim a protection is bypassed merely because Frida attached successfully. Do not claim a control is effective because the app did not crash.

## Excluded techniques

No instructions or scripts for bypassing certificate pinning, root/emulator checks, anti-debugging, anti-tamper, authentication, licensing, payment, or entitlement controls in production third-party apps. No token/credential extraction, persistence, stealth or out-of-scope testing.

If an owner needs a controlled bypass validation for their own test build, require a separate written authorization, a dedicated lab fixture and security review. Keep the result confined to that fixture.

## Evidence schema

~~~json
{
  "evidence_type": "android.protection_resilience_test",
  "engagement_id": "…",
  "apk_sha256": "…",
  "package_name": "…",
  "control_id": "tls_trust_validation",
  "test_case_id": "…",
  "expected_outcome": "…",
  "observed_outcome": "…",
  "assessment": "effective|ineffective|inconsistent|not_tested|inconclusive",
  "evidence_refs": [],
  "false_positive_notes": [],
  "coverage_limitations": []
}
~~~

## Acceptance tests

- Require explicit control-resilience scope and test-case approval.
- Reject production targets without specific authorization for the test.
- Ensure hooks observe but do not alter control return values.
- Ensure reports distinguish not-tested from pass.
- Test repeatability, false-positive notes, redaction and evidence provenance.
