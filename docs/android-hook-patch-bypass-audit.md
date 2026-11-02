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

Observe selected lifecycle, app API, network metadata, cryptographic API metadata, storage operation metadata, and app-reported trust-control outcomes. The default mode is metadata-only. Hook templates must be reviewed, version-controlled, hash-pinned and approved. The baseline must not alter method arguments or return values.

### Patch integrity audit

Compare the original and modified artifacts without changing either input. Report added/removed/changed archive members, manifest and permission deltas, DEX/native/resource changes, package identity and signer verification status. A provider that is unavailable must produce an explicit unknown result; inventory of signing files is not cryptographic signature verification.

### Protection resilience audit

Evaluate root/emulator/debugger/instrumentation detection, APK integrity, TLS trust validation and runtime tamper response using purpose-built lab fixtures or owner-provided test builds. Report whether each documented expected behavior was observed. A Frida attach is not proof of bypass; an app crash is not proof of an effective defense.

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

**Added in this change:** versioned Skill playbooks, evidence schemas, workflows, risk boundaries and acceptance-test requirements.

**Not implemented yet:** executable Frida templates/runtime, ADB adapter, emulator manager, original-versus-patched APK diff engine, DEX/resource diff providers, cryptographic signer verification, automated protection test harness, evidence graph and finding generator.

Do not advertise these playbooks as live capabilities. A feature is implemented only after code, automated tests, isolated integration tests and a verified CI run.

## Implementation sequence

1. Build a typed Frida observation adapter with reviewed template registry and mock transport tests.
2. Build isolated disposable-emulator lifecycle and bounded ADB adapter.
3. Add APK artifact-pair records and ZIP/manifest comparison.
4. Add sandboxed DEX/resource/native providers and cryptographic signer verification.
5. Add owner-controlled protection test fixtures and resilience outcome reporting.
6. Connect evidence provenance and findings to the existing tenant-scoped audit model.
