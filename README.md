# SockBoi AI

**Policy-first AI security assessment platform.** SockBoi AI coordinates authorized security reviews using scoped assets, approval gates, specialist-agent planning, evidence provenance, and auditable workflows.

> **Status: v0.2.0 developer preview.** The agent planner creates structured assessment plans; it does not yet execute scanner, browser, MCP, LLM, or network tools. Authentication, durable persistence, and production isolation are not implemented.

## Included

- FastAPI service and interactive API docs.
- Engagement and explicit asset-scope models.
- Central policy checks and human approval records.
- Deterministic multi-agent planner endpoint: POST /engagements/{id}/plan?target=...
- Specialist roles for Guard, Hunter, API, Network, and Analyst.
- Technique catalog for scope review, supplied API schema review, HTTP/TLS review planning, supplied network inventory review, and evidence integrity.
- Audit events, findings, Docker development stack, and unit tests.

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

## Agent planning workflow

1. Create an engagement with a written authorization reference and exact assets.
2. Request a plan for an asset explicitly included in that engagement.
3. Review the proposed specialist-agent steps and risk classifications.
4. Record human approval before any future active adapter is allowed to execute.
5. Review audit events and findings.

The planner only creates a plan. It does not initiate network requests or run tools.

## Security model

- No implicit wildcard or subdomain expansion.
- Out-of-scope assets are rejected by deterministic policy.
- Active and state-changing actions require explicit approval.
- No arbitrary shell, reverse shell, credential theft, persistence, destructive testing, or denial-of-service capability.
- Imported skills, webpages, and model output are untrusted data and cannot modify policy.
- Never commit secrets, credentials, customer data, or real engagement evidence.

## Important limitations

This developer preview uses an in-memory store, has no authentication or tenant isolation, and does not yet persist data to PostgreSQL. Docker Compose provisions development dependencies only. Do not expose it to the public internet or use it for production assessments.

## Roadmap

- [x] API and policy foundation
- [x] Deterministic specialist-agent plan builder
- [x] Technique catalog and audit events
- [ ] PostgreSQL persistence, migrations, RBAC, tenant isolation
- [ ] HackSkills ingestion and hybrid retrieval
- [ ] Typed MCP adapters and browser/ZAP integrations
- [ ] Evidence storage and report generation
- [ ] Optional LLM planner constrained by deterministic policy

See docs/architecture.md, docs/agent-system.md, and SECURITY.md.

## License

MIT.
