---
name: container-kubernetes-review
version: 0.1.0
description: Review container images, manifests, and cluster configuration supplied by the operator.
asset_types: [container_image, kubernetes_cluster, manifest_bundle]
risk: passive
---

# Container and Kubernetes Review

## Workflow
1. Review Dockerfiles, image metadata, SBOMs, and dependency manifests.
2. Inspect Kubernetes RBAC, pod security settings, network policies, secrets references, and exposed services from supplied manifests.
3. Identify privileged containers, host namespace usage, writable root filesystems, and excessive capabilities.
4. Review image provenance, signing, and vulnerability scan exports.
5. Produce evidence-backed remediation guidance.

## Safety
Do not deploy workloads, access cluster secrets, execute images, or alter cluster state.
