---
name: android-control-resilience
version: 1.0.0
description: Assess whether Android security controls fail safely under authorized, controlled negative-test scenarios.
allowed_asset_types: [android-apk, android-emulator, android-device]
risk_class: high
requires_human_approval: [control_test.run, frida.instrumentation.attach, device_state.change]
---

# Android Security-Control Resilience Assessment

## Purpose

Evaluate whether an application's security controls enforce the intended policy under controlled, authorized test conditions. This Skill reports control strength and observed failure modes; it does not provide reusable bypass payloads or instructions to defeat third-party applications.

## Test domains

- Root and device-integrity policy.
- Emulator and test-environment policy.
- Debugger and instrumentation policy.
- TLS certificate and hostname validation.
- Authentication and authorization enforcement.
- Local data protection and backup policy.
- Deep-link, exported-component, and IPC authorization.
- Tamper detection and update/signature policy.

## Controlled test design

For every control, record:
- Expected policy and documented user impact.
- Exact app build SHA-256 and package identity.
- Test device/emulator fingerprint and state.
- Preconditions and approved test scenario.
- Observation-only Frida script ID and SHA-256, if used.
- Expected secure behavior and observed behavior.
- Evidence reference, confidence, and coverage limitations.

Use a purpose-built test build or a lab app with explicit test toggles. For TLS tests, use a test CA and test endpoint controlled by the engagement owner. For authentication/authorization, use designated test accounts and non-production records. Do not intercept unrelated traffic or collect real credentials.

## Result states

- resistant: the control enforced the documented policy in the tested scenario.
- weak: the control failed in the tested scenario with reproducible evidence.
- inconclusive: test conditions, instrumentation, or evidence were insufficient.
- not_tested: no approved execution occurred.

A static string, method name, or Frida hook attachment is not proof that a control was bypassed. A test is not successful merely because instrumentation was loaded.

## Frida constraints

Use reviewed, hash-pinned observation scripts only. Capture method identity and event metadata, not secret values. Do not alter return values, skip security checks, disable certificate validation, suppress integrity checks, or extract credentials. Any behavior-changing experiment must use a purpose-built lab build with an explicit test seam and separate approval.

## Reporting

For each control, report expected behavior, test setup, actual observations, result state, reproducibility, impact, remediation, and untested paths. Keep facts separate from hypotheses. Never claim a control is resistant based only on absence of observed failure.
