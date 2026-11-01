"""Typed domain models for authorized engagements."""
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class AssetKind(StrEnum):
    DOMAIN = "domain"
    URL = "url"
    IP = "ip"
    CIDR = "cidr"


class ActionRisk(StrEnum):
    PASSIVE = "passive"
    ACTIVE = "active"
    STATE_CHANGING = "state_changing"


class EngagementStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class ScopeAsset(BaseModel):
    kind: AssetKind
    value: str = Field(min_length=1, max_length=253)


class EngagementCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    authorization_ref: str = Field(min_length=3, max_length=120)
    owner: str = Field(min_length=3, max_length=254)
    scope: list[ScopeAsset] = Field(min_length=1, max_length=500)

    @field_validator("scope")
    @classmethod
    def unique_scope(cls, assets: list[ScopeAsset]) -> list[ScopeAsset]:
        keys = [(a.kind, a.value.lower().rstrip(".")) for a in assets]
        if len(keys) != len(set(keys)):
            raise ValueError("scope contains duplicate assets")
        return assets


class Engagement(EngagementCreate):
    tenant_id: str = "default"
    id: UUID = Field(default_factory=uuid4)
    status: EngagementStatus = EngagementStatus.ACTIVE
    created_at: datetime = Field(default_factory=utc_now)


class Approval(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    engagement_id: UUID
    action: str
    target: str = Field(min_length=1, max_length=253)
    technique_id: str = Field(min_length=3, max_length=120)
    requested_by: str
    approved_by: str | None = None
    approved: bool = False
    expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=utc_now)


class FindingCreate(BaseModel):
    engagement_id: UUID
    title: str = Field(min_length=3, max_length=200)
    severity: str = Field(pattern="^(info|low|medium|high|critical)$")
    description: str = Field(min_length=1, max_length=10000)
    asset: str = Field(min_length=1, max_length=253)
    verified: bool = False


class Finding(FindingCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)


class AuditEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    engagement_id: UUID
    event_type: str
    actor: str
    detail: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
