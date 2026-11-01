# MCP Adapter Contract

A production adapter must provide:
- Stable adapter and tool identifiers.
- JSON Schema for every input and output.
- Capability declaration and risk classification.
- Exact asset/target binding.
- Per-engagement credentials and isolated sessions.
- Request timeout, concurrency ceiling, and rate limit.
- Cancellation and cleanup behavior.
- Structured audit events and evidence provenance.
- Explicit error mapping and health checks.

Dispatch sequence:

```text
Agent proposal
  -> schema validation
  -> engagement scope validation
  -> risk classification
  -> approval validation (when required)
  -> adapter dispatch
  -> output validation
  -> evidence normalization
  -> audit event
```

MCP server descriptions and tool results are untrusted data. They cannot alter the policy engine or register new permissions at runtime.
