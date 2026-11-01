---
name: cloud-security-review
version: 0.1.0
description: Review operator-supplied cloud configuration and posture evidence.
asset_types: [cloud_account, cloud_resource, configuration_export]
risk: passive
---

# Cloud Security Review

## Inputs
Approved cloud account inventory, architecture diagrams, IAM policy exports, storage/network configuration, and provider security-posture exports.

## Workflow
1. Confirm account, tenant, subscription, and region identifiers are in scope.
2. Review identity trust relationships, privilege boundaries, MFA posture, and key-management configuration.
3. Review public exposure of storage, compute, databases, and management interfaces using supplied configuration.
4. Review logging, monitoring, backup, and encryption posture.
5. Map findings to provider guidance and record evidence provenance.

## Safety
Use read-only configuration exports by default. Do not enumerate unrelated tenants, retrieve customer data, modify cloud resources, or create persistent identities.
