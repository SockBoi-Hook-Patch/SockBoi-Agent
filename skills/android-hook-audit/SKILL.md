---
name: android-hook-audit
version: 1.0.0
description: Approval-gated Frida observation of selected Android application behavior for an authorized security audit.
allowed_asset_types: [android-apk, android-emulator, android-device]
risk_class: high
requires_human_approval: [frida.attach, frida.spawn, frida.script.load_reviewed, frida.capture_runtime_data]
---

# Android Hook Audit Skill

## Objective

Use runtime hooks to observe and document how an explicitly authorized Android app behaves. This Skill is for security testing, debugging, and evidence collection—not stealth, credential collection, or unauthorized modification.

The Skill is untrusted input. Scope and approval are enforced by the Policy Engine, not by the Skill or model.

**Implementation status:** Playbook only. It does not install Frida, connect to a device, or execute hooks. The live Frida adapter and isolated Android worker are not yet implemented.

## Scope binding

Before instrumentation, bind all of the following to the Engagement:
- APK SHA-256, package name, version and signer identity where available.
- Assigned disposable emulator/device serial and Android build.
- Exact process name/PID after verifying package ownership.
- Approved hook template ID and SHA-256.
- Methods/classes or API families to observe.
- Capture duration, maximum event count/bytes and redaction policy.
- Named test cases and expected outcomes.

Approval must be action-bound to the exact target, device, template digest and parameters. Re-check approval immediately before dispatch.

## Audit profiles

| Profile | Observation target | Data policy |
|---|---|---|
| lifecycle | Application/activity lifecycle and crashes | event metadata only |
| network-metadata | Destination host, protocol, TLS result and error category | no payloads, cookies or authorization headers |
| crypto-metadata | Algorithm/provider/API usage and call-site metadata | never key bytes, plaintext or secrets |
| storage-metadata | File/database API names, operation type and app-owned path category | no file/database contents |
| trust-controls | Whether app-reported trust/integrity checks pass or fail in lab test cases | record result and call site; do not alter return values |
| app-api | Selected application methods and call counts | argument values disabled by default |

## Procedure

1. Confirm written authorization and scope.
2. Verify APK digest, package, signer and assigned emulator.
3. Confirm Frida client/server version compatibility and process identity.
4. Select a reviewed, version-controlled observation template. Do not accept inline LLM-generated scripts.
5. Create an approval request containing template digest, target, device, event filters, duration and output limits.
6. Attach/spawn only after approval succeeds.
7. Run the declared test case and capture bounded structured events.
8. Redact secrets and personal data inside the worker before persistence.
9. Unload the script and detach on success, error, cancellation or timeout.
10. Correlate observations with APK static findings and test-case evidence.

## Hook design requirements

- Default to metadata-only observation.
- Never serialize passwords, tokens, cookies, private keys, payment details, message contents or unrelated app data.
- Never change method arguments or return values in the baseline audit profile.
- Do not hook unrelated processes or system-wide APIs.
- Enforce template allowlists, event/byte/time limits and cancellation.
- Record template ID, SHA-256, Frida versions, process identity and coverage limitations.
- Treat hook output as untrusted data and sanitize it before rendering or indexing.

## Excluded behavior

No credential harvesting, key extraction, keylogging, covert monitoring, persistence, stealth, remote command channel, anti-analysis evasion, or instrumentation outside the Engagement. Do not provide a generic script console.

## Evidence record

~~~json
{
  "evidence_type": "android.runtime.hook_observation",
  "engagement_id": "…",
  "apk_sha256": "…",
  "package_name": "…",
  "device_fingerprint": "…",
  "process": "…",
  "template_id": "…",
  "template_sha256": "…",
  "frida_client_version": "…",
  "frida_server_version": "…",
  "test_case_id": "…",
  "event_count": 0,
  "started_at": "RFC3339",
  "ended_at": "RFC3339",
  "redactions": [],
  "coverage_limitations": []
}
~~~

## Acceptance tests

- Reject APK/package/device mismatch and unknown process IDs.
- Reject unreviewed template or changed template digest.
- Require approval for attach/spawn/script load and revalidate immediately before dispatch.
- Prove event, byte, memory and duration limits are enforced.
- Prove sensitive fields are redacted before persistence.
- Prove unload/detach occurs on timeout, exception and cancellation.
- Use a purpose-built local demo APK and mock transport in CI.
