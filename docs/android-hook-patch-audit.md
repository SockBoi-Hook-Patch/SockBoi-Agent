# Android Hook, Patch, and Control-Resilience Audit

## Status

This milestone adds:
- A read-only APK build comparison endpoint.
- A Frida observation-only Java method hook template.
- A control-resilience assessment Skill for authorized lab scenarios.
- A patch provenance and evidence workflow.

It does not add a generic APK patcher, APK re-signer, live Frida/ADB runtime, or bypass payload library. The Frida template is a reviewed example and is not executed by the API.

## Read-only patch audit

Endpoint: POST /engagements/{engagement_id}/apk/patch-audit

Multipart fields:
- original_file: original APK
- patched_file: candidate patched APK

The endpoint validates both APKs using bounded ZIP inspection, streams each member through SHA-256, and reports added, removed, and changed archive entries grouped by category. It records an audit event containing artifact hashes and change counts. It does not persist the APK bytes, extract files, modify either artifact, or execute app code.

This comparison detects byte-level changes only. It is not semantic DEX diffing and does not verify APK cryptographic signatures.

## Hooking

The Frida example at skills/frida-android-runtime/templates/java-method-observer.js observes one named Java method and emits method identity, argument types, return type, and call/return events. It does not log argument values or alter return values. Before any future execution:
1. Adapt it only to the authorized lab APK.
2. Review the final script.
3. Compute and pin its SHA-256.
4. Bind the exact script digest, app digest, device, and operation parameters to action approval.
5. Enforce event/byte/time limits, redaction, and detach on all exit paths.

## Bypass assessment

The control-resilience Skill defines test cases and result states for root/integrity, emulator, debugger, TLS validation, authentication/authorization, storage, exported components, and tamper controls. Use purpose-built lab builds, test endpoints, and designated test accounts. The system records whether a control resisted or failed under a documented scenario; it does not distribute bypass code or silently change app behavior.

## Release gates for live runtime

- Isolated Android worker and disposable emulator.
- Typed ADB/Frida adapters; no generic shell or arbitrary script execution.
- Reviewed and hash-pinned script catalogue.
- Action-bound human approval immediately before attach/spawn/script dispatch.
- Tenant and Engagement checks for all artifacts, jobs, and evidence.
- Resource quotas, cancellation, redaction, deterministic cleanup.
- Local fixture APK integration tests and CI.
- Separate security review before enabling any behavior-changing lab test.

## Limitations

No live hook, patch, bypass, APK repackage, signing, install, or runtime test is performed by this API. Patch comparison is offline and read-only. Frida/ADB execution remains a future adapter milestone.
