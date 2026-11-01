# Contributing to SockBoi Agent

Thank you for considering a contribution. SockBoi Agent is an early-stage security-assessment planning project. Contributions should improve correctness, clarity, testability, and enforceable security boundaries.

## Project status

The current v0.3.1 release is a **Developer Preview**, not a production-ready assessment platform. It has no API authentication, user-level RBAC, tenant isolation, durable storage, live MCP execution, or scanner integration. Do not describe planned capabilities as implemented.

## Non-negotiable design principles

- **Explicit authorization:** assessment targets must be covered by a clearly defined engagement scope and written permission.
- **Policy is authoritative:** Agent/LLM output, Skills, and Knowledge are untrusted inputs. They must never override policy decisions.
- **Human approval:** active or state-changing operations must require explicit human review and approval before execution.
- **Least privilege:** integrations must expose only the capabilities required for their task.
- **Tenant isolation:** future multi-user features must enforce isolation at the data-access boundary, not only in prompts or UI.
- **Auditability:** security-relevant decisions and actions should be attributable and reviewable.
- **Safe defaults:** deny by default when scope, identity, approval, or policy context is missing or ambiguous.

Do not introduce unrestricted shell execution, arbitrary tool dispatch, credential theft, persistence, destructive actions, denial-of-service functionality, or out-of-scope operations.

## Development setup

Requirements: Python 3.12+

```bash
git clone https://github.com/SockBoi-Hook-Patch/SockBoi-Agent.git
cd SockBoi-Agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
```

## Quality checks

Run the relevant checks before submitting:

```bash
pytest
ruff check .
```

Add or update tests for behavior changes, especially around:

- Scope matching and normalization.
- Approval lifecycle, identity, expiry, and action binding.
- Policy decisions and deny-by-default behavior.
- Tenant and engagement data isolation.
- Untrusted Skills/Knowledge handling.
- Audit event creation and integrity.

Do not claim that tests or security checks passed unless you ran them and can report the result. If a check cannot be run, state that clearly in the pull request.

## Pull request guidelines

A useful pull request includes:

1. **Problem:** what is incorrect, missing, or risky?
2. **Changes:** what was changed and why?
3. **Tests:** exact commands run and their results.
4. **Security impact:** new capabilities, trust boundaries, permissions, and failure modes.
5. **Documentation:** relevant README, architecture, API, or security-policy updates.
6. **Compatibility:** configuration, migration, and API behavior changes.

Keep pull requests focused and reasonably small. Avoid mixing unrelated refactors with security-sensitive changes.

## Reporting vulnerabilities

Do not open a public issue containing exploit details, credentials, personal data, or third-party evidence. Follow the private reporting guidance in [SECURITY.md](SECURITY.md).

## Contributor recognition

GitHub derives the repository's Contributors list from commit history. There is no manually maintained contributor roster. Use the GitHub account identity you want associated with your commits and pull requests; do not rewrite history merely to change contributor counts.
