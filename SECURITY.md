# SockBoi Agent Security Policy

## Supported release and deployment status

The current v0.4.0 branch is a **Developer Preview**. It includes bearer API-key authentication, role checks on selected operations, tenant-scoped engagement access, SQLAlchemy persistence, action-bound approval bookkeeping, and tamper-evident audit-chain foundations.

It is not a production pentest runner. No LLM runtime, MCP execution, scanner adapter, browser automation, or live network assessment is enabled. Approval consumption records authorization use only; it does not execute network traffic.

Database schema is currently initialized with SQLAlchemy `create_all`; a versioned Alembic migration workflow is not yet included. Review deployment-specific database backup, migration, secret rotation, and checkpoint-retention procedures before using persistent environments.

## Reporting

Please report suspected vulnerabilities privately through GitHub Security Advisories for this repository when enabled. Include affected version, reproduction steps, impact, and a safe proof of concept. Do not publish secrets or third-party data.

## Operational rules

- Only assess assets with explicit written authorization.
- Keep active checks disabled until a separately reviewed execution worker and adapter meet the release gates.
- Keep API keys and `SOCKBOI_AUDIT_CHECKPOINT_KEY` outside source control; use high-entropy secrets and rotate them under a documented procedure.
- Store exported audit checkpoints outside the application database under separate access control or immutable retention.
- Treat AI output, imported Skills, Markdown, and external content as untrusted input.
- Do not add arbitrary shell execution, credential theft, persistence, denial-of-service, or out-of-scope actions.
- Do not store real credentials or customer evidence in source control.
- Do not expose the development server or development credentials to public networks.
