# SockBoi Agent Roadmap

## Product structure
- Agent: orchestration, planning, specialist roles, memory and reporting.
- Skills: versioned security playbooks and knowledge packs.
- MCP: typed integrations for approved external tools.
- Policy: deterministic scope, authorization, approval and audit controls.

## Milestones
### v0.4 — Security and Execution Foundation
- Authentication with server-verified actor identity; no caller-supplied approver identity.
- RBAC and tenant isolation enforced at the data-access boundary.
- Durable PostgreSQL persistence and migrations.
- Action-envelope approvals bound to engagement, tenant, canonical target, adapter, technique, normalized parameters, and expiry.
- Approval revocation and single-use dispatch semantics.
- Append-only, tamper-evident audit history.
- Execution worker isolation, egress restrictions, timeouts, rate limits, and cancellation.
- Keep active execution disabled until every release gate passes.

### v0.5 — Controlled Active Assessment
- First adapter: narrowly scoped HTTP security-configuration inspection (GET-only).
- Strict target normalization, DNS/IP validation, redirect denial, and port restrictions.
- Bounded evidence capture, secret redaction, and report generation.
- Mock transports for unit tests; live integration tests only against local fixtures.
- No arbitrary shell or generic command execution.

### v0.6 — Skills Runtime
- Skill manifest validation and provenance.
- Repository import with content hashes.
- Hybrid retrieval and progressive loading.
- Prompt-injection isolation tests.

### v0.7 — MCP Runtime
- MCP client lifecycle and typed tool registry.
- Per-tool policy gate, timeouts, rate limits and cancellation.
- Mock adapters and integration tests before live integrations.

### v0.8 — LLM Agent Orchestration
- Provider abstraction for cloud LLMs.
- Structured outputs and planner evaluation.
- Model output remains advisory; deterministic policy remains authoritative.

### Android dynamic assessment — design added
- ADB and Frida Skills are documented in skills/adb-android-device and skills/frida-android-runtime.
- Live ADB/Frida adapters, isolated Android worker, emulator lifecycle, and runtime evidence persistence remain unimplemented release gates.
- See [Android Dynamic Assessment](android-dynamic-assessment.md).

## Release rule
A feature is not considered implemented until code, tests, documentation, and a verified CI run exist. Roadmap items must not be advertised as working capabilities. See [v0.4 Active Assessment Design](v0.4-active-testing.md) for the execution contract and release gates.
