"""Immutable action-envelope approval primitives."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class ActionEnvelope:
    engagement_id: str
    tenant_id: str
    target: str
    adapter_id: str
    technique_id: str
    parameters: dict
    risk: str

    def digest(self) -> str:
        canonical = json.dumps(
            asdict(self), sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class ApprovalGrant:
    envelope_sha256: str
    requester: str
    reviewer: str
    expires_at: datetime
    approval_id: str
    revoked: bool = False
    consumed: bool = False


def validate_approval(envelope: ActionEnvelope, grant: ApprovalGrant, now: datetime | None = None) -> None:
    """Validate an approval against the exact action; caller must atomically consume it."""
    current = now or datetime.now(UTC)
    if grant.revoked:
        raise PermissionError("approval has been revoked")
    if grant.consumed:
        raise PermissionError("approval has already been consumed")
    if grant.requester == grant.reviewer:
        raise PermissionError("requester and reviewer must be different actors")
    if grant.expires_at.tzinfo is None:
        raise PermissionError("approval expiry must be timezone-aware")
    if grant.expires_at <= current:
        raise PermissionError("approval has expired")
    if not hashlib.sha256(envelope.digest().encode()).hexdigest() == hashlib.sha256(
        grant.envelope_sha256.encode()
    ).hexdigest():
        raise PermissionError("approval does not match the requested action envelope")
