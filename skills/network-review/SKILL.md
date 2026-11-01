---
name: network-inventory-review
version: 0.1.0
description: Analyze operator-provided network and service inventory.
asset_types: [ip, cidr]
risk: passive
---

# Network Inventory Review

## Inputs
Operator-provided asset list, service inventory, configuration exports, and network diagrams.

## Workflow
1. Validate that each asset is explicitly listed in the engagement scope.
2. Normalize IP addresses, CIDRs, service names, and observed versions.
3. Identify exposed management planes, legacy protocols, and unnecessary service exposure from supplied evidence.
4. Correlate observations with vendor advisories supplied or retrieved through approved sources.
5. Record uncertainty where version or reachability evidence is incomplete.

## Output
Asset, observed service, evidence source, exposure rationale, confidence, and mitigation.

## Safety
This Skill is inventory analysis only. It does not initiate port scans, exploit services, or access systems.
