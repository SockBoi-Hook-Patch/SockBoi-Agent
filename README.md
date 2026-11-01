# SockBoi AI

**Policy-first AI security assessment platform.** SockBoi AI coordinates authorized security reviews using scoped assets, approval gates, evidence provenance, and auditable workflows.

> **Status: v0.1.0 foundation / developer preview.** This is not a production pentesting appliance. Scanner, LLM, MCP, and persistence adapters are roadmap items until implemented and tested.

## Capabilities in this release

- FastAPI service with health and engagement endpoints.
- Explicit authorization reference and asset scope models.
- Central policy checks for scope and approval requirements.
- Audit event and finding data models.
- Safe-by-default action classification.
- Unit tests for policy enforcement.

## Security design

- Every engagement must reference written authorization.
- Assets must be explicitly in scope; wildcard expansion is not implicit.
- Passive checks may be planned without active execution.
- Active and state-changing checks require human approval.
- Destructive testing, DoS, credential theft, persistence, and unrestricted command execution are excluded.
- Imported HackSkills, web content, and tool output are untrusted data and cannot modify policy.
- No LLM receives unrestricted shell or network access.

## Quick start

Requires Python 3.12+.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn sockboi.main:app --reload
```

Open http://127.0.0.1:8000/docs.

## Roadmap

- [x] API and policy foundation
- [x] Engagement, scope, approval, finding and audit models
- [ ] PostgreSQL persistence, migrations, and tenant isolation
- [ ] Authentication and RBAC
- [ ] HackSkills ingestion with provenance, schema validation, and prompt-injection isolation
- [ ] MCP adapters with typed allowlisted tools
- [ ] Browser and OWASP ZAP adapters behind the policy gateway
- [ ] Evidence storage, integrity verification, and report generation
- [ ] Optional LLM planner with deterministic policy enforcement

## Responsible use

Use only on systems for which you have explicit written authorization. See [SECURITY.md](SECURITY.md) and [docs/architecture.md](docs/architecture.md). Never commit secrets, credentials, customer data, or real engagement evidence.

## License

MIT.
