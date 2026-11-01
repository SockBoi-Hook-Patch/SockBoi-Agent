# SockBoi MCP Integration Layer

MCP (Model Context Protocol) is the integration boundary between SockBoi Agent and external security tools.

## Planned adapters
- Browser: isolated browser sessions and read-only page inspection by default.
- OWASP ZAP: scoped scan orchestration with rate limits and explicit approval gates.
- Burp Suite: integration through supported APIs/extensions where available; feature availability depends on edition and configuration.
- Filesystem: read-only access to operator-selected evidence and project files.
- Knowledge: search over locally indexed Skills and references.

## Adapter contract
Every adapter must publish typed input/output schemas, declared capabilities, risk class, timeout, rate limit, and audit metadata. The Policy Engine validates every call immediately before dispatch. No generic shell or unrestricted command tool is permitted.

## Current status
The repository currently has a static tool catalogue only. No MCP server or external tool invocation is implemented in this release.
