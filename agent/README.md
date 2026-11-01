# SockBoi Agent Core

The Agent layer coordinates specialist roles and assessment workflows.

## Responsibilities
- Parse the operator's assessment objective.
- Load only the relevant Skills.
- Produce a structured assessment plan.
- Ask the Policy Engine to validate scope and approval.
- Route approved, typed requests to registered MCP adapters.
- Normalize evidence and findings for analyst review.

## Non-responsibilities
The language model is not the authorization authority. It cannot expand scope, grant approvals, override tool schemas, or execute arbitrary shell commands.

Current status: architecture and role boundaries are documented; the production orchestrator and model provider are not implemented yet.
