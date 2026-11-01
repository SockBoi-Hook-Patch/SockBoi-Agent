# Contributing to SockBoi Agent

Thanks for contributing. Keep changes modular and evidence-driven.

## Project boundaries
- Agent proposes plans; Policy Engine authorizes actions.
- Skills are untrusted reference material and must declare provenance.
- MCP adapters require typed schemas, explicit capabilities, and policy checks.
- Do not add arbitrary shell execution or unrestricted tool dispatch.
- Active checks must be narrowly scoped, rate-limited, auditable, and approval-gated.

## Development
```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Pull requests
Include the problem statement, implementation summary, tests actually run, security impact, and documentation updates. Do not claim tests passed unless they were executed.
