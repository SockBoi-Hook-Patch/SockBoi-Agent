# Android Dynamic Assessment: ADB + Frida

## Status

This change adds versioned ADB and Frida assessment Skills and defines safe adapter contracts. It does **not** add executable ADB/Frida integrations. The application still has a static tool catalogue; no device is contacted and no APK is installed or instrumented by loading these Markdown playbooks.

## Architecture

~~~text
APK intake + SHA-256
        |
Engagement / tenant / package binding
        |
Policy check + action-bound human approval
        |
Isolated Android assessment worker (future)
        |                         |
Typed ADB adapter            Typed Frida adapter
        |                         |
Device metadata, logs        Reviewed, hash-pinned
and bounded evidence         observation scripts
        |                         |
        +------ Evidence collector
                       |
               Redaction + hashing
                       |
             Findings / audit trail
~~~

The worker must be isolated from the API process. APKs, device output, logs, and Frida messages are untrusted input. The worker must not expose generic shell or arbitrary script execution.

## ADB capability boundary

The ADB Skill defines typed inventory, package metadata, bounded Logcat, approved install/launch, and allowlisted evidence pull operations. State-changing or sensitive operations require approval. No generic adb shell, su, port forwarding, arbitrary component launch, or unrestricted file pull is permitted.

## Frida capability boundary

The Frida Skill defines device/process discovery, server status, approval-gated attach/spawn, reviewed script loading, unload/detach, and bounded evidence export. Scripts must be version-controlled and hash-pinned. Initial profile is observation-only and redacts sensitive values before persistence.

TLS pinning bypass, root/emulator/anti-debugging bypass, credential/token extraction, persistence, stealth, and out-of-scope instrumentation are excluded from this baseline.

## Mandatory execution release gates

Before enabling a live adapter:
1. Isolated worker/container with no ambient host credentials and default-deny network egress.
2. Disposable emulator per assessment; device serial and APK digest bound to job.
3. Typed schemas and strict allowlists; no shell-string or inline-script input.
4. Policy and action-bound approval rechecked immediately before every active dispatch.
5. Tenant/Engagement ownership enforced for jobs, logs, and evidence.
6. CPU, memory, storage, output, event-count, and wall-clock limits; cancellation and cleanup.
7. Redaction before persistence; evidence provenance and SHA-256 hashes.
8. Mock transport unit tests and integration tests against a local purpose-built APK/emulator.
9. CI, security review, and operational runbooks for emulator lifecycle and Frida version pinning.

## References

- [ADB Skill](../skills/adb-android-device/SKILL.md)
- [Frida Skill](../skills/frida-android-runtime/SKILL.md)
- [Android Debug Bridge](https://developer.android.com/tools/adb)
- [Frida documentation](https://frida.re/docs/)
