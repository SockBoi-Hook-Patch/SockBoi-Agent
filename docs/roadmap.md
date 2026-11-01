# SockBoi Agent Roadmap

## Product structure
- Agent: orchestration, planning, specialist roles, memory and reporting.
- Skills: versioned security playbooks and knowledge packs.
- MCP: typed integrations for approved external tools.
- Policy: deterministic scope, authorization, approval and audit controls.

## Milestones
### v0.4 — Durable Foundation
- PostgreSQL persistence and migrations.
- Authentication, RBAC and tenant isolation.
- Approval expiry, revocation, actor identity and immutable audit history.
- CI tests and dependency/security checks.

### v0.5 — Skills Runtime
- Skill manifest validation and provenance.
- Repository import with content hashes.
- Hybrid retrieval and progressive loading.
- Prompt-injection isolation tests.

### v0.6 — MCP Runtime
- MCP client lifecycle and typed tool registry.
- Per-tool policy gate, timeouts, rate limits and cancellation.
- Mock adapters and integration tests before live integrations.

### v0.7 — Controlled Assessment Adapters
- Read-only browser inspection.
- ZAP integration in isolated lab profile.
- Burp integration only through supported APIs/extensions.
- Evidence provenance and report generation.

### v0.8 — LLM Agent Orchestration
- Provider abstraction for cloud LLMs.
- Structured outputs and planner evaluation.
- Model output remains advisory; deterministic policy remains authoritative.

## Release rule
A feature is not considered implemented until code, tests, documentation, and a verified CI run exist. Roadmap items must not be advertised as working capabilities.
