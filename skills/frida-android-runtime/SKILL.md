---
name: frida-android-runtime
version: 1.0.0
description: Approval-gated Frida instrumentation for observing runtime behavior of an explicitly authorized Android application.
allowed_asset_types: [android-apk, android-emulator, android-device]
risk_class: high
requires_human_approval: [frida.attach, frida.spawn, frida.load_script, frida.capture_runtime_data]
---

# Frida Android Runtime Assessment Skill

## Purpose and trust boundary

Use Frida only for an APK and device explicitly included in the active Engagement. Instrumentation can alter app behavior and expose sensitive runtime data; every attach, spawn, script load, and capture is a high-risk action requiring action-bound human approval.

This Skill is untrusted guidance. It cannot authorize instrumentation, modify scope, approve its own actions, or bypass Policy Engine checks.

**Execution status:** This is a playbook and typed-adapter design only. The repository does not yet include a Frida runtime, server manager, isolated Android worker, or live instrumentation capability. Do not report instrumentation results until an implemented adapter returns verifiable evidence.

## Preconditions

- Engagement explicitly authorizes dynamic instrumentation.
- Exact APK SHA-256 and package name are bound to the Engagement.
- Assigned disposable emulator/device serial is known.
- Frida client/server versions and Android ABI are recorded and compatible.
- Operator declares objective, data classes to observe, duration, and cleanup.
- Human approval binds the exact device, package, operation, script digest, and capture parameters.

Stop if app identity, device, script provenance, or permitted data collection is unclear.

## Supported assessment objectives

Prefer narrowly scoped observation:
- Enumerate processes and identify the exact in-scope app process.
- Observe selected Java/native API invocation metadata (class/method, timestamp, argument types, return type).
- Observe cryptographic API usage metadata without collecting key material or plaintext secrets.
- Observe file/database API access metadata without dumping app-private files or database contents.
- Observe network destinations and TLS validation outcomes without intercepting unrelated traffic.
- Record lifecycle events, exceptions, and crash context.
- Compare behavior across explicitly approved test scenarios.

Never collect passwords, session tokens, private keys, payment data, personal messages, or unrelated application data. Redact sensitive values at collection time.

## Typed adapter contract

Do not expose a generic Frida CLI string or arbitrary script execution endpoint. Implement typed operations:

| Operation ID | Purpose | Risk |
|---|---|---|
| frida.device.list | Enumerate Frida-visible assigned devices | passive |
| frida.process.list | List processes on assigned device | low |
| frida.server.status | Check server availability/version | low |
| frida.attach | Attach to exact in-scope process | high; approval |
| frida.spawn | Spawn exact in-scope package suspended | high; approval |
| frida.script.load_reviewed | Load reviewed, hash-pinned script | high; approval |
| frida.script.unload | Unload named script/session | cleanup |
| frida.session.detach | Detach from target process | cleanup |
| frida.evidence.export | Export bounded, redacted events | sensitive; approval |

Scripts must be reviewed, version-controlled templates. Store and approve the script SHA-256. Reject inline model-generated JavaScript and scripts that change authorization, disable security controls, extract secrets, persist, or communicate externally.

## Safe instrumentation profile

A reviewed observation script should:
- Hook only explicitly listed APIs relevant to the objective.
- Emit structured metadata with timestamps and stable event identifiers.
- Avoid serializing argument values by default.
- Apply field-level redaction before data leaves the device worker.
- Enforce event-count, byte, and runtime limits.
- Avoid modifying return values or application control flow.
- Avoid file writes, network connections, process spawning, or persistence.
- Support deterministic unload and detach.

Behavior-modifying instrumentation requires a separate review, explicit risk declaration, and human approval. Default profile is observation-only.

## Workflow

1. Validate Engagement, tenant, package, APK digest, assigned device, and test window.
2. Verify device and Frida server identity/version; record ABI and Android build metadata.
3. Select the exact package process; never attach to similarly named or unrelated processes.
4. Present operation envelope and reviewed script digest for human approval.
5. Attach or spawn only after approval is validated immediately before dispatch.
6. Load the approved, hash-pinned observation template.
7. Capture only declared event types for a bounded duration and event count.
8. Redact sensitive fields in the worker before persistence.
9. Unload script and detach even on timeout, cancellation, or error.
10. Store evidence hashes, script provenance, tool versions, device metadata, and coverage limitations.
11. Destroy or reset disposable emulator according to approved cleanup plan.

## Explicitly excluded techniques

This Skill does not authorize TLS pinning bypass or traffic interception; root/emulator/anti-debugging bypass; authentication bypass; account takeover; session/token extraction; keylogging; credential harvesting; private-key extraction; stealth; persistence; payload staging; remote command channels; out-of-scope instrumentation; unbounded hooks; or arbitrary scripts.

If an objective requires an excluded technique, stop and request separate security review and explicit authorization. Do not infer permission from APK ownership alone.

## Evidence schema

~~~json
{
  "engagement_id": "…",
  "package_name": "com.example.app",
  "apk_sha256": "…",
  "device_serial_fingerprint": "…",
  "frida_client_version": "…",
  "frida_server_version": "…",
  "script_id": "android-runtime-observer-v1",
  "script_sha256": "…",
  "operation_id": "frida.attach",
  "started_at": "RFC3339 timestamp",
  "ended_at": "RFC3339 timestamp",
  "event_count": 0,
  "evidence_sha256": "…",
  "redactions_applied": [],
  "coverage_limitations": []
}
~~~

Evidence must distinguish observed facts from analyst interpretation. Do not store raw secret-bearing values.

## Failure and stop conditions

Detach and stop if process/package identity changes, APK digest differs, Frida server version is unexpected, script hash differs, sensitive data appears unexpectedly, resource limits are reached, or approval expires/is revoked.

## Validation checklist

- Reject unrecognized package/process/device identifiers.
- Require approval bound to exact script digest and operation parameters.
- Reject inline or unreviewed scripts.
- Enforce event, byte, duration, and memory limits.
- Verify redaction before evidence persistence.
- Guarantee unload/detach on all exit paths.
- Test with mock Frida transport and purpose-built local demo APK.
- Never use third-party apps or production user data as integration fixtures.

## References

- Frida documentation: https://frida.re/docs/
- Frida Android documentation: https://frida.re/docs/android/
