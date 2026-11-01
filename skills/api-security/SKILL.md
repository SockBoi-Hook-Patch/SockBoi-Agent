---
name: api-security-review
version: 0.1.0
description: Review supplied API schemas and authorized API behavior.
asset_types: [url, domain]
risk: mixed
---

# API Security Review

## Inputs
OpenAPI/Swagger, GraphQL schema, endpoint inventory, authorization model, and explicitly approved test accounts.

## Workflow
1. Parse the supplied schema and normalize endpoints and methods.
2. Identify authentication requirements and object-, function-, and property-level authorization boundaries.
3. Review input validation, mass assignment, rate-limit design, error handling, and sensitive-data exposure.
4. Build a test matrix using synthetic or approved accounts and records.
5. Label each proposed check passive or active; active checks require target-specific approval.
6. Capture minimal evidence and avoid accessing unrelated user data.

## Output
Endpoint matrix, control observations, evidence references, impact, confidence, and remediation.

## Safety
No credential stuffing, data exfiltration, destructive mutation, or testing outside the engagement scope.
