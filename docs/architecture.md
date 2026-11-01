# Architecture

## Design

SockBoi AI is intended to be a control plane, not an autonomous unrestricted exploit runner.

```text
Dashboard / API
      |
Engagement & Authorization
      |
Central Policy Gate ---- Audit Log
      |
Typed Tool Adapters (planned)
  |        |         |
Browser   ZAP      MCP Skills
      |
Evidence Store (planned)
      |
Analyst Review & Report (planned)
```

## Non-negotiable boundaries

1. Engagements require an authorization reference and explicit assets.
2. Scope checks are deterministic and independent of LLM output.
3. Tool adapters accept typed arguments and enforce allowlists.
4. Active actions require an unexpired, engagement-bound approval.
5. Imported skill documents and web content are untrusted data; they cannot issue instructions to the orchestrator.
6. No arbitrary shell, raw script execution, reverse shell, persistence, credential theft, or denial-of-service capability is provided.

## Current implementation limits

The current store is process-local memory. API endpoints have no user authentication. The Compose database and Redis are development dependencies only and are not wired into the store. There are no functioning scanner, browser, MCP, LLM, or evidence-storage adapters in this version.

## Planned execution lifecycle

Authorization -> scope validation -> passive discovery -> asset inventory -> skill retrieval -> test plan -> approval checkpoint -> constrained adapter -> evidence capture -> analyst verification -> report.

## Planned advanced techniques

- Hybrid knowledge retrieval (BM25 + embeddings) with source provenance.
- Progressive skill loading to avoid dumping entire repositories into model context.
- Differential web/API testing with rate limits and explicit test accounts.
- Browser-based authenticated test flows isolated per engagement.
- Passive TLS, HTTP security-header, and endpoint configuration review.
- Evidence integrity hashes and reproducible finding records.
- Attack-surface graph and relationship-based prioritization.
- Confidence scoring that separates observed facts from hypotheses.

These are roadmap items, not claims of implemented functionality.
