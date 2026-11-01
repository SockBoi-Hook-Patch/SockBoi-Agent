"""Deterministic policy gate. This module never performs network activity."""
from datetime import UTC, datetime
from ipaddress import ip_address, ip_network
from urllib.parse import urlparse

from .models import ActionRisk, Approval, AssetKind, Engagement, ScopeAsset


class PolicyDenied(Exception):
    """Raised when an action violates engagement policy."""


def _normalize_domain(value: str) -> str:
    return value.strip().lower().rstrip(".")


def asset_matches(scope: ScopeAsset, target: str) -> bool:
    """Exact matching only; CIDR supports IP containment, never implicit subdomain expansion."""
    if scope.kind == AssetKind.DOMAIN:
        candidate = _normalize_domain(target)
        if "://" in candidate:
            candidate = (urlparse(candidate).hostname or "").lower()
        return candidate == _normalize_domain(scope.value)
    if scope.kind == AssetKind.URL:
        return target.rstrip("/") == scope.value.rstrip("/")
    if scope.kind == AssetKind.IP:
        try:
            return ip_address(target) == ip_address(scope.value)
        except ValueError:
            return False
    if scope.kind == AssetKind.CIDR:
        try:
            return ip_address(target) in ip_network(scope.value, strict=False)
        except ValueError:
            return False
    return False


def is_in_scope(engagement: Engagement, target: str) -> bool:
    return any(asset_matches(asset, target) for asset in engagement.scope)


def authorize_action(
    engagement: Engagement,
    target: str,
    risk: ActionRisk,
    approval: Approval | None = None,
    technique_id: str | None = None,
) -> None:
    if not is_in_scope(engagement, target):
        raise PolicyDenied("target is not explicitly in engagement scope")
    if risk == ActionRisk.PASSIVE:
        return
    if approval is None or not approval.approved:
        raise PolicyDenied("active actions require explicit human approval")
    if approval.engagement_id != engagement.id:
        raise PolicyDenied("approval belongs to a different engagement")
    if approval.target.lower().rstrip("/") != target.lower().rstrip("/"):
        raise PolicyDenied("approval is bound to a different target")
    if technique_id is None or approval.technique_id != technique_id:
        raise PolicyDenied("approval is bound to a different technique")
    if approval.requested_by == approval.approved_by:
        raise PolicyDenied("requester cannot approve their own request")
    if approval.expires_at and approval.expires_at <= datetime.now(UTC):
        raise PolicyDenied("approval has expired")
