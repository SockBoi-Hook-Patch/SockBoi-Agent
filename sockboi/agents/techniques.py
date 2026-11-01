"""Curated technique catalog. Entries describe plans; they do not execute tools."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Technique:
    id: str
    title: str
    description: str
    asset_kinds: tuple[str, ...]
    risk: str
    approval_required: bool
    category: str


TECHNIQUES: tuple[Technique, ...] = (
    Technique("inventory.scope_review", "Scope and asset inventory review",
              "Normalize supplied assets and identify missing ownership or scope metadata.",
              ("domain", "url", "ip", "cidr"), "passive", False, "governance"),
    Technique("web.headers_review", "HTTP security-header review",
              "Review supplied HTTP response headers for common defensive configuration gaps.",
              ("domain", "url"), "active", True, "web"),
    Technique("web.tls_review", "TLS configuration review",
              "Assess TLS protocol and certificate configuration for the scoped endpoint.",
              ("domain", "url"), "active", True, "web"),
    Technique("api.schema_review", "API schema review",
              "Review a user-provided OpenAPI or GraphQL schema for design and authorization risks.",
              ("url", "domain"), "passive", False, "api"),
    Technique("network.exposure_review", "Network exposure review",
              "Review a supplied port/service inventory; this plan does not initiate port scans.",
              ("ip", "cidr"), "passive", False, "network"),
    Technique("evidence.integrity_check", "Evidence integrity verification",
              "Verify hashes and provenance metadata for evidence already collected by the operator.",
              ("domain", "url", "ip", "cidr"), "passive", False, "evidence"),
)


def techniques_for(asset_kind: str) -> list[Technique]:
    return [tech for tech in TECHNIQUES if asset_kind in tech.asset_kinds]
