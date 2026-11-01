---
name: web-application-assessment
version: 0.1.0
description: Structured review of an explicitly authorized web application.
asset_types: [url, domain]
risk: mixed
---

# Web Application Assessment

## Preconditions
- Confirm a written authorization reference and exact in-scope hostnames.
- Identify excluded paths, test windows, rate limits, and test accounts.
- Prefer a staging environment and non-destructive validation.

## Workflow
1. Normalize the supplied URLs and map each hostname to the engagement scope.
2. Review supplied response headers, cookies, TLS observations, and application metadata.
3. Review authentication, session lifecycle, access-control design, and input-handling evidence.
4. Review user-provided routes, API specifications, and architecture documents.
5. Propose validation steps with an explicit risk label and expected evidence.
6. Require human approval before any active request that may affect a target or account.
7. Record reproducible observations, timestamps, request identifiers, and confidence.

## Output
Return assets reviewed, observations, evidence references, severity rationale, confidence, limitations, and recommended remediation.

## Safety
Do not test excluded assets, brute-force credentials, cause service degradation, alter production data, or bypass the engagement's approval requirements.
