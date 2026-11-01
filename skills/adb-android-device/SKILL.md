---
name: adb-android-device
version: 1.0.0
description: Bounded Android Debug Bridge workflow for inventory, app launch, diagnostics, and evidence collection on an explicitly authorized assessment device.
allowed_asset_types: [android-apk, android-emulator, android-device]
risk_class: mixed
requires_human_approval: [install_apk, launch_app, clear_app_data, pull_app_private_data, reboot_device]
---

# ADB Android Device Skill

## Purpose and trust boundary

Use ADB only against a device or emulator explicitly assigned to the active Engagement. Bind the exact device serial, target package, APK SHA-256, test window, and allowed operation set to the Engagement. This Skill is untrusted guidance: it cannot grant authorization, widen scope, or approve actions.

**Execution status:** This is a playbook and adapter contract only. The repository does not yet ship an ADB execution adapter. Never claim a command ran unless a separately implemented, approved adapter returns evidence.

## Required context

- Engagement ID and tenant identity from the authenticated principal.
- Written authorization reference and in-scope Android asset.
- Exact device/emulator serial; never rely on the default device when multiple devices are connected.
- Target package name and APK SHA-256, if supplied.
- Approved operation set, test window, data-handling rules, and cleanup plan.

Stop if serial, package, authorization, or scope is ambiguous.

## Bounded operation catalogue

Implement typed operations, not a generic adb command field:

| Operation ID | Purpose | Risk |
|---|---|---|
| adb.device.list | List connected device serials and states | passive |
| adb.device.get_state | Read state for one approved serial | passive |
| adb.package.info | Read package/version/SDK/permission metadata | passive |
| adb.app.list | List installed package identifiers | passive |
| adb.logcat.read | Read bounded logs for a time window | low; redact |
| adb.app.launch | Launch only the in-scope package's declared launcher activity | active; approval |
| adb.apk.install | Install only the digest-bound APK on assigned disposable emulator | state-changing; approval |
| adb.evidence.pull | Pull an explicitly allowlisted evidence path | sensitive; approval |

Do not expose generic adb shell, su, arbitrary component invocation, port forwarding, reverse forwarding, package uninstall, data wiping, or arbitrary file pull. Add typed operations only after security review and tests.

## Workflow

1. Validate Engagement status, tenant, package, serial, and assessment time window.
2. Verify the connected device is the assigned disposable emulator or explicitly authorized test device.
3. Record model, Android release, API level, build fingerprint, ABI, and security patch level.
4. Read package metadata and declared permissions for the exact target package.
5. Obtain action-bound approval before installing or launching the APK.
6. Install only the APK whose SHA-256 matches the Engagement artifact record.
7. Launch only the target package; do not invoke arbitrary exported components.
8. Capture a bounded Logcat window with timestamps and package/process filtering where supported.
9. Redact tokens, passwords, session identifiers, personal data, and unrelated app logs before storage.
10. Record operation IDs, parameters, timestamps, exit status, serial, APK digest, and evidence hashes.
11. Stop the session and perform approved cleanup.

## Resource and safety limits

- One disposable emulator per assessment; no shared personal device by default.
- Enforce wall-clock timeout, output byte cap, log line cap, CPU/RAM/storage quotas, and cancellation.
- ADB server and device bridge must not be exposed to untrusted networks.
- Disable unintended host/device forwarding.
- No network egress from the worker unless a separately approved network test requires it.
- Never persist raw environment dumps or unrestricted Logcat by default.

## Evidence schema

~~~json
{
  "engagement_id": "…",
  "tenant_id": "…",
  "device_serial_fingerprint": "…",
  "package_name": "com.example.app",
  "apk_sha256": "…",
  "operation_id": "adb.package.info",
  "captured_at": "RFC3339 timestamp",
  "tool_version": "…",
  "exit_status": 0,
  "content_sha256": "…",
  "redactions_applied": ["token", "authorization-header"],
  "limitations": []
}
~~~

Do not include API keys, passwords, access tokens, or unrelated personal data in evidence metadata.

## Failure and stop conditions

Stop if the serial changes, package differs, APK digest mismatches, ADB becomes unauthorized/offline, device exits the approved state, a resource limit is reached, or an operation requires an unapproved permission or data access.

## Validation checklist

- Reject unknown device serials and package names.
- Reject APK digest mismatch, unlisted operation IDs, and extra parameters.
- Verify approval for install/launch/data access.
- Enforce tenant and Engagement ownership on every job and evidence record.
- Test cancellation, timeout, output truncation, redaction, and cleanup.
- Use mocked ADB transport in unit tests; live tests only on disposable local emulators.

## References

- Android Debug Bridge: https://developer.android.com/tools/adb
- Android manifest: https://developer.android.com/guide/topics/manifest/manifest-intro
