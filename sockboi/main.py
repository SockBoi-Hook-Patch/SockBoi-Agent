"""SockBoi AI HTTP API."""
from uuid import UUID

from fastapi import FastAPI, HTTPException

from . import __version__
from .models import (
    ActionRisk, Approval, AuditEvent, Engagement, EngagementCreate,
    Finding, FindingCreate,
)
from .policy import PolicyDenied, authorize_action
from .store import store

app = FastAPI(
    title="SockBoi AI",
    version=__version__,
    description="Policy-first control plane foundation for authorized security assessments.",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "sockboi-ai", "version": __version__}


@app.post("/engagements", response_model=Engagement, status_code=201)
def create_engagement(payload: EngagementCreate) -> Engagement:
    engagement = Engagement(**payload.model_dump())
    store.engagements[engagement.id] = engagement
    store.log(AuditEvent(
        engagement_id=engagement.id, event_type="engagement.created",
        actor=engagement.owner, detail={"authorization_ref": engagement.authorization_ref},
    ))
    return engagement


@app.get("/engagements", response_model=list[Engagement])
def list_engagements() -> list[Engagement]:
    return list(store.engagements.values())


@app.get("/engagements/{engagement_id}", response_model=Engagement)
def get_engagement(engagement_id: UUID) -> Engagement:
    item = store.engagements.get(engagement_id)
    if item is None:
        raise HTTPException(404, "engagement not found")
    return item


@app.post("/engagements/{engagement_id}/approvals", response_model=Approval, status_code=201)
def request_approval(engagement_id: UUID, action: str, requested_by: str) -> Approval:
    if engagement_id not in store.engagements:
        raise HTTPException(404, "engagement not found")
    item = Approval(engagement_id=engagement_id, action=action, requested_by=requested_by)
    store.approvals[item.id] = item
    store.log(AuditEvent(
        engagement_id=engagement_id, event_type="approval.requested",
        actor=requested_by, detail={"approval_id": str(item.id), "action": action},
    ))
    return item


@app.post("/approvals/{approval_id}/decide", response_model=Approval)
def decide_approval(approval_id: UUID, approved_by: str, approved: bool) -> Approval:
    item = store.approvals.get(approval_id)
    if item is None:
        raise HTTPException(404, "approval not found")
    item.approved = approved
    item.approved_by = approved_by
    store.log(AuditEvent(
        engagement_id=item.engagement_id, event_type="approval.decided",
        actor=approved_by, detail={"approval_id": str(item.id), "approved": approved},
    ))
    return item


@app.post("/policy/check")
def policy_check(
    engagement_id: UUID, target: str, risk: ActionRisk, approval_id: UUID | None = None
) -> dict:
    engagement = store.engagements.get(engagement_id)
    if engagement is None:
        raise HTTPException(404, "engagement not found")
    approval = store.approvals.get(approval_id) if approval_id else None
    try:
        authorize_action(engagement, target, risk, approval)
    except PolicyDenied as exc:
        store.log(AuditEvent(
            engagement_id=engagement_id, event_type="policy.denied",
            actor="api", detail={"target": target, "risk": risk.value, "reason": str(exc)},
        ))
        raise HTTPException(403, str(exc)) from exc
    store.log(AuditEvent(
        engagement_id=engagement_id, event_type="policy.allowed",
        actor="api", detail={"target": target, "risk": risk.value},
    ))
    return {"allowed": True, "target": target, "risk": risk.value}


@app.post("/findings", response_model=Finding, status_code=201)
def create_finding(payload: FindingCreate) -> Finding:
    engagement = store.engagements.get(payload.engagement_id)
    if engagement is None:
        raise HTTPException(404, "engagement not found")
    if not any(a.value.lower() == payload.asset.lower() for a in engagement.scope):
        raise HTTPException(403, "finding asset must match an explicitly scoped asset")
    finding = Finding(**payload.model_dump())
    store.findings[finding.id] = finding
    store.log(AuditEvent(
        engagement_id=engagement.id, event_type="finding.created",
        actor="api", detail={"finding_id": str(finding.id), "severity": finding.severity},
    ))
    return finding


@app.get("/engagements/{engagement_id}/audit", response_model=list[AuditEvent])
def get_audit(engagement_id: UUID) -> list[AuditEvent]:
    if engagement_id not in store.engagements:
        raise HTTPException(404, "engagement not found")
    return [event for event in store.audit if event.engagement_id == engagement_id]
