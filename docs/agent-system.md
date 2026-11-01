# SockBoi Agent System (v0.2 roadmap foundation)

## Current implementation

The deterministic planner converts an in-scope asset into typed work items assigned to specialist agent roles. It only creates a plan; it does not invoke browsers, scanners, shells, external APIs, or arbitrary tools. Each step records its technique identifier, target, risk, approval requirement, and execution state.

## Agent roles

- **SockBoi Core:** orchestration and lifecycle management (planned).
- **SockBoi Guard:** scope, authorization, approval, and policy enforcement.
- **SockBoi Recon:** asset inventory and supplied metadata analysis (planned).
- **SockBoi Hunter:** web configuration and application review (approval-gated adapter planned).
- **SockBoi API:** schema and API design review (planned).
- **SockBoi Network:** review of operator-supplied service inventories (planned).
- **SockBoi Analyst:** evidence integrity, confidence, and finding verification (planned).
- **SockBoi Report:** report generation (planned).

## Technique catalog

The initial catalog includes scope inventory, supplied API schema review, HTTP security-header review, TLS configuration review, supplied network inventory review, and evidence integrity verification. The catalog is deliberately declarative: a technique description is not executable code.

## Autonomy model

1. The planner may create a proposed plan for an explicitly scoped asset.
2. Passive analysis of user-supplied material may be marked as not requiring active-test approval.
3. Any network interaction or state-changing test must go through a separately implemented adapter and the central policy gate.
4. Active steps require an approval bound to the engagement, target, technique, and expiry before execution. This foundation does not yet implement adapter execution.
5. The model cannot add scope, grant approvals, or change policy.

## Next engineering milestones

- Persist plans and task state in PostgreSQL with tenant isolation.
- Add authenticated users, roles, and approval identity.
- Bind approvals to exact targets and technique IDs, with expiry and revocation.
- Add read-only evidence import and SHA-256 integrity metadata.
- Add sandboxed browser/ZAP adapters with egress allowlists and rate limits.
- Add skill retrieval with provenance, content validation, and prompt-injection isolation.
- Add evaluation datasets and regression tests for planner quality.
