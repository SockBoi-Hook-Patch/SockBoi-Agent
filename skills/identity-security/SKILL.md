---
name: identity-and-directory-review
version: 0.1.0
description: Review supplied identity, directory, and access-control configuration.
asset_types: [identity_tenant, directory_export, configuration_bundle]
risk: passive
---

# Identity and Directory Security Review

## Workflow
1. Confirm tenant and directory identifiers are explicitly in scope.
2. Review role assignments, privileged groups, service identities, trust relationships, and stale accounts in supplied exports.
3. Review authentication policy, MFA coverage, conditional access, and recovery controls.
4. Identify excessive privileges and segregation-of-duties gaps.
5. Provide least-privilege remediation with evidence references.

## Safety
Use read-only exports. Do not attempt password attacks, token theft, account takeover, persistence, or changes to identity configuration.
