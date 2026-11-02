# SockBoi Agent Roadmap

## Product structure
- Agent: orchestration, planning, specialist roles, and reporting.
- Skills: versioned, provenance-aware playbooks loaded progressively.
- MCP / adapters: typed integrations for approved external tools.
- Policy: deterministic scope, authorization, approval and audit controls.
- Evidence: artifact identity, observations, findings, provenance and coverage.

## Milestones

### v0.4 — Security and Execution Foundation
- Authentication, RBAC, tenant isolation, durable persistence, action-bound approval and tamper-evident audit foundation.
- Active execution remains disabled until release gates pass.

### v0.5 — Controlled Active Assessment
- Scoped HTTP inspection, isolated worker, DNS/SSRF/redirect controls, egress allowlist, timeouts and rate limits.
- Bounded evidence capture and redaction.

### v0.6 — Skills Runtime
- Skill manifest validation, provenance, repository import, hybrid retrieval and prompt-injection isolation.

### v0.7 — MCP Runtime
- Typed tool registry, per-tool policy gate, timeout, cancellation and mock adapters.

### v0.8 — LLM Agent Orchestration
- Provider abstraction and structured outputs; model output remains advisory.

### Android / APK assessment — staged capability

- APK triage and specialist Skill taxonomy: added.
- Safe offline APK ZIP inspection library and tenant-scoped inspect endpoint: included in the pending Android foundation PR; confirm CI and merge before treating as mainline.
- ADB and Frida playbooks: added; live adapters remain unimplemented.
- Hook Audit, Patch Integrity Audit and Protection Resilience Audit playbooks: added in this PR update.
- Static providers (JADX, Apktool/aapt2, DEX/resource/native diff, cryptographic APK signer verification): planned.
- Evidence graph, case router, dynamic emulator worker, Frida instrumentation runtime and automated resilience test harness: planned.
- Flutter, Unity/IL2CPP, React Native and native analysis provider integrations: planned.

See [APK Reverse Engineering Roadmap](apk-reverse-engineering-roadmap.md), [Android Dynamic Assessment](android-dynamic-assessment.md), and [Hook, Patch and Protection Audit](android-hook-patch-bypass-audit.md).

## Release rule
A feature is implemented only when code, tests, documentation and a verified CI run exist. Playbooks and roadmap entries must not be advertised as executable capabilities.
