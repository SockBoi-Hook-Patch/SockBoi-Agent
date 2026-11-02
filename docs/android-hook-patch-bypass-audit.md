# Android Hook, Patch and Protection Audit

## Scope

This capability set extends APK assessment with three distinct audit workflows:

1. **Runtime Hook Audit** — observe selected app behavior with reviewed Frida templates.
2. **Patch Integrity Audit** — compare an owner-supplied original APK with an owner-supplied modified APK and explain artifact deltas.
3. **Protection Resilience Audit** — evaluate whether documented controls respond correctly under approved lab test conditions.

The terms "patch" and "bypass" describe audit subjects and test outcomes. This baseline does not generate modified APKs or provide operational bypass recipes for production third-party applications.

## Skills

- [Android Hook Audit](../skills/android-hook-audit/SKILL.md)
- [Android Patch Integrity Audit](../skills/android-patch-integrity-audit/SKILL.md)
- [Android Protection Resilience Audit](../skills/android-protection-resilience-audit/SKILL.md)
- [ADB Android Device](../skills/adb-android-device/SKILL.md)
- [Frida Android Runtime](../skills/frida-android-runtime/SKILL.md)

## Intended workflow

~~~text
Original APK + modified APK (optional)
             |
      APK SHA-256 identity
             |
    Engagement / tenant scope
             |
     Policy + human approval
             |
    Disposable Android lab
        |            |
   ADB adapter   Frida adapter
        |            |
   Device/logs    Reviewed observation hooks
        |            |
        +---- Evidence collector
                    |
         Redaction + provenance hashes
                    |
          Findings + coverage report
~~~

## Audit capabilities

### Hook audit

Observe selected lifecycle, app API, network metadata, cryptographic API metadata, storage operation metadata, and app-reported trust-control outcomes. The intended Frida profile is metadata-only. Hook templates must be reviewed, version-controlled, hash-pinned and approved. They must not alter method arguments or return values.

**Current status:** The Hook Audit Skill is a playbook only. No Frida client, device transport, template registry, or live hook execution is included.

### Patch integrity audit

The code now provides offline APK comparison through:

`POST /engagements/{engagement_id}/apk/compare`

Submit two multipart files named `original_file` and `modified_file`. The endpoint:
- enforces the existing per-file APK size limit and ZIP safety checks;
- computes independent SHA-256 digests;
- compares archive members and reports added, removed and changed entries;
- flags security-relevant paths such as the manifest, DEX, native libraries, signing metadata and network-security resources;
- reports package identity match when both manifests are parseable;
- emits a tenant-scoped audit event with artifact hashes and change counts.

The comparison reads bounded ZIP members in memory; it does not extract files to disk, execute either APK, modify source artifacts, or generate an output APK. It identifies DEX/native changes by member digest only; it does not decompile code or establish semantic changes. APK signer cryptographic validity remains **not verified**.

### Protection resilience audit

Evaluate root/emulator/debugger/instrumentation detection, APK integrity, TLS trust validation and runtime tamper response using purpose-built lab fixtures or owner-provided test builds. Report whether each documented expected behavior was observed. A Frida attach is not proof of bypass; an app crash is not proof of an effective defense.

**Current status:** Test methodology is documented, but there is no automated protection test harness or live Frida runtime. No production bypass mechanism is provided.

## Policy and safety requirements

- Every test is bound to an Engagement, tenant, APK SHA-256, package, device serial, test case and time window.
- Approval is action-bound to exact operation parameters and reviewed script digest.
- Re-check approval immediately before active dispatch.
- Use disposable emulators and isolate the worker from the API process.
- No generic ADB shell, arbitrary Frida script console or model-generated inline script execution.
- No credential/token/key extraction, stealth, persistence, destructive patching, licensing/payment circumvention or out-of-scope instrumentation.
- Redact secrets before evidence persistence.
- Enforce event, byte, CPU, memory, storage and wall-clock limits; guarantee detach and cleanup.
- Store provenance, tool versions, script hashes, input artifact hashes and coverage limitations.

## Current implementation status

**Implemented in code on this feature branch:**
- Safe offline APK ZIP inspection and tenant-scoped `/apk/inspect` endpoint (from the parent Android foundation PR).
- Offline original-versus-modified APK member comparison and tenant-scoped `/apk/compare` endpoint.
- SHA-256 provenance, bounded upload handling, ZIP safety validation, package identity comparison where parseable, and audit events.
- Unit and API tests for member deltas, package mismatch, malformed APKs, size limits and tenant isolation.

**Playbooks only / not live execution:** ADB adapter, emulator manager, Frida runtime, reviewed script registry, runtime hook execution, protection-resilience automation and bypass testing.

**Still planned:** DEX/resource semantic diff providers, cryptographic APK signer verification, isolated Android worker, evidence graph and automated finding generation.

Do not advertise playbooks as live capabilities. A feature is implemented only after code, automated tests, isolated integration tests and a verified CI run.

## Implementation sequence

1. Build a typed Frida observation adapter with reviewed template registry and mock transport tests.
2. Build isolated disposable-emulator lifecycle and bounded ADB adapter.
3. Add sandboxed DEX/resource/native providers and cryptographic signer verification.
4. Add owner-controlled protection test fixtures and resilience outcome reporting.
5. Connect evidence provenance and findings to the existing tenant-scoped audit model.
