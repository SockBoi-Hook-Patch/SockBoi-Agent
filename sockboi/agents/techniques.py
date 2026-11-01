"""Curated technique catalog. Entries describe plans; they do not execute tools."""
from dataclasses import dataclass
from . import __name__ as _package_name


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
    Technique(
        id="inventory.scope_review", title="Scope and asset inventory review",
        description="Normalize the supplied asset and identify missing ownership or scope metadata.",
        asset_kinds=("domain", "url", "ip", "cidr"), risk="passive",
        approval_required=False, category="governance",
    ),
    Technique(
        id="web.headers_review", title="HTTP security-header review",
        description="Review supplied HTTP response headers for common defensive configuration gaps.",
        asset_kinds=("domain", "url"), risk="active",
        approval_required=True, category="web",
    ),
    Technique(
        id="web.tls_review", title="TLS configuration review",
        description="Assess TLS protocol and certificate configuration for the explicitly scoped endpoint.",
        asset_kinds=("domain", "url"), risk="active",
        approval_required=True, category="web",
    ),
    Technique(
        id="api.schema_review", title="API schema review",
        description="Review a user-provided OpenAPI or GraphQL schema for design and authorization risks.",
        asset_kinds=("url", "domain"), risk="passive",
        approval_required=False, category="api",
    ),
    Technique(
        id="network.exposure_review", title="Network exposure review",
        description="Review a supplied port/service inventory; this plan does not initiate port scans.",
        asset_kinds=("ip", "cidr"), risk="passive",
        approval_required=False, category="network",
    ),
    Technique(
        id="evidence.integrity_check", title="Evidence integrity verification",
        description="Verify hashes and provenance metadata for evidence already collected by the operator.",
        asset_kinds=("domain", "url", "ip", "cidr"), risk="passive",
        approval_required=False, category="evidence",
    ),
)


def techniques_for(asset_kind: str) -> list[Technique]:
    return [tech for tech in TECHNIQUES if asset_kind in tech.asset_kinds]
