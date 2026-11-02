# SockBoi Agent Roadmap

**Status snapshot:** 2026-11-02  
**Default branch:** `main`  
**Package version on main:** `0.4.0` (`pyproject.toml`)  
**Project status:** Developer Preview; active execution adapters are not enabled.

This roadmap distinguishes code merged into `main` from open pull requests, design documents, and future work. A Skill or design document is not an executable capability.

## Product tracks

- **Agent:** planning and orchestration. Integrated LLM runtime is not implemented.
- **Skills:** versioned security playbooks and specialist knowledge; treat content as untrusted.
- **MCP / adapters:** typed external-tool integrations behind deterministic policy gates; live execution is not implemented.
- **Policy:** authentication, RBAC, tenant isolation, scope, human approval and audit.
- **Android / APK:** safe static intake first, then isolated static providers and finally controlled dynamic lab execution.
- **Evidence:** artifact identity, provenance, observations, findings, coverage, and reproducible reporting.

## Current mainline status

### Implemented in main

| Area | Current implementation | Important limitation |
|---|---|---|
| Security foundation | API-key authentication, selected RBAC, tenant-scoped Engagement and Knowledge | Production hardening and broader authorization review remain |
| Approval | Action-bound approval, expiry, one-time consume, self-approval protection | Consume is bookkeeping; no adapter is dispatched |
| Persistence | SQLAlchemy-backed Engagement, Approval, Finding and Audit Event records | Uses `create_all`; Alembic migration workflow is not implemented |
| Audit | Engagement-scoped hash-chain verification and HMAC checkpoint export | External checkpoint retention/monitoring is operational responsibility |
| Planner / Knowledge | Scope-aware plan and tenant-scoped Markdown keyword search | No integrated LLM agent runtime or vector/hybrid retrieval |
| Tool registry | Typed tool catalogue | Execution disabled |
| APK intake | `POST /engagements/{id}/apk/inspect`; bounded ZIP inspection, SHA-256, DEX/native/resource/asset inventory and plain-text XML manifest parsing | No APK persistence/extraction/execution, binary XML decode, DEX decompile, or cryptographic signer verification |

## Milestones

### v0.4 — Security and persistence foundation
<badge>Implemented in main</badge>

- Fail-closed API-key authentication.
- Role checks and tenant isolation for implemented endpoints.
- Durable SQLAlchemy persistence for core assessment records.
- Action-bound, one-time human approval.
- Engagement-scoped audit hash chain and HMAC checkpoint export.
- APK static ZIP inspection endpoint added after the initial v0.4 foundation.
- Package version remains 0.4.0; no release tag is implied by merge.

### v0.5 — APK static analysis and artifact integrity
<badge color="warning">In progress</badge>

**Already in main**
- Safe APK upload and bounded ZIP inspection.
- SHA-256 artifact identity and archive inventory.
- Limited plain-text XML manifest summary.
- Engagement audit event for inspection.

**Pending / under review**
- Read-only original-versus-modified APK archive comparison.
- Added/removed/changed archive member report and artifact provenance.
- Observation-only Frida Java hook example and lab control-resilience Skill.

Open work at the snapshot:
- [PR #5 — APK hook and patch audit foundation](https://github.com/SockBoi-Hook-Patch/SockBoi-Agent/pull/5): open; targets the Android feature branch rather than main; GitHub reported it as not mergeable at the time checked. Resolve/rebase before considering it for mainline.
- [PR #6 — offline APK patch integrity audit](https://github.com/SockBoi-Hook-Patch/SockBoi-Agent/pull/6): open; targets the Android feature branch; mergeability was reported true, but CI/status checks were not returned by the available status query. Review its diff and validation before merging.

**Remaining v0.5 work**
- Reconcile PR #5 and #6 into one canonical patch-audit API/implementation; avoid shipping duplicate endpoints with overlapping purpose.
- Add durable artifact records if retention is required; current inspect endpoint does not persist uploaded APK bytes.
- Decode binary AndroidManifest.xml using a pinned, isolated provider.
- Add DEX/resource/native analysis providers (JADX, Apktool/aapt2, ELF/JNI) with timeouts, output caps and no network by default.
- Add cryptographic APK signature verification; do not treat ZIP signature-file presence as proof of validity.
- Add test coverage for malformed archives, ZIP bombs, path traversal, duplicate entries, oversized uploads, tenant isolation and audit integrity.

### v0.6 — Static reverse-engineering providers and case workflow
<badge color="secondary">Planned</badge>

- Sandboxed, pinned JADX and Apktool/aapt2 providers.
- DEX class/method/reference navigation and decompilation.
- Resource/string/locale analysis and binary manifest decoding.
- Native ELF/ABI/JNI inventory and bounded analysis.
- Cryptographic APK signature and signer-lineage verification.
- Evidence graph: artifact → observation → finding → remediation.
- Master/category/specialist Skill router with scope and provenance state.
- Finding confidence, false-positive handling, coverage and report export.

### v0.7 — Android dynamic assessment foundation
<badge color="secondary">Planned</badge>

- Isolated Android assessment worker, separate from FastAPI process.
- Disposable emulator lifecycle and device identity binding.
- Typed ADB adapter: device inventory, package metadata, approved install/launch, bounded Logcat and allowlisted evidence transfer.
- Job cancellation, CPU/memory/storage/time/output quotas and cleanup.
- Default-deny worker egress and no generic ADB shell endpoint.
- Mock ADB transport tests and local emulator integration tests.

### v0.8 — Frida runtime and observation-based Hook Audit
<badge color="secondary">Planned</badge>

- Pinned Frida client/server compatibility and device readiness checks.
- Reviewed, version-controlled, hash-pinned script registry.
- Typed attach/spawn/load/unload/detach operations with action-bound approval.
- Observation-only Java/native hook profiles and bounded structured event capture.
- Redaction before evidence persistence; no inline model-generated script execution.
- Deterministic detach and cleanup on timeout, cancellation or failure.
- Local demo APK and disposable emulator integration tests.

### v0.9 — Protection resilience and patch intelligence
<badge color="secondary">Planned</badge>

- Owner-controlled lab builds and documented expected control behavior.
- Test harness for root/emulator/debugger/instrumentation policy, TLS validation, tamper response and app integrity.
- Report effective / ineffective / inconsistent / not tested / inconclusive; do not infer bypass from a crash or a single instrumentation result.
- Semantic DEX/resource/native diff and verified signer comparison.
- Patch provenance, findings correlation and reproducible audit report.
- No generalized bypass payload library, credential extraction, stealth, persistence, destructive modification, or payment/licensing circumvention.

### v1.0 — Agent, MCP and controlled execution integration
<badge color="secondary">Planned</badge>

- LLM provider abstraction and structured planning outputs.
- MCP client lifecycle and typed tool registration.
- Per-tool policy gate, approval revalidation immediately before dispatch, timeouts, rate limits, cancellation and audit.
- Isolated worker orchestration and execution provenance.
- Evaluation suite, deployment hardening, database migrations, operational monitoring and external checkpoint retention.
- Release only after security review and complete CI/integration acceptance.

## Cross-cutting release gates

No active adapter may be enabled until all relevant gates pass:

1. **Authorization:** explicit Engagement scope, authenticated tenant, exact asset identity and approved test window.
2. **Action approval:** approval bound to operation, target, normalized parameters and script/tool digest; rechecked immediately before dispatch.
3. **Isolation:** workers separate from API, disposable targets, no ambient credentials and default-deny network egress.
4. **Input safety:** APKs, logs, model output, Skills and tool output are untrusted; validate schemas and provenance.
5. **Resource limits:** wall-clock, CPU, memory, storage, output/event count, concurrency and cancellation.
6. **Evidence:** redact secrets before persistence; retain artifact/script/tool hashes and coverage limitations.
7. **Tenant security:** enforce tenant and Engagement ownership on every job, artifact, evidence and finding read/write.
8. **Testing:** mock transport tests, adversarial archive tests, tenant-isolation tests and local purpose-built APK/emulator integration tests.
9. **Operations:** cleanup, retention, migrations, monitoring, incident response and security review.

## Release accuracy rule

A capability is marked **Implemented** only when code is merged into `main`, tests exist, CI passes, and the actual runtime behavior is verified. Open PRs are not mainline features. Skills, examples, diagrams and roadmap items are not executable tools.
