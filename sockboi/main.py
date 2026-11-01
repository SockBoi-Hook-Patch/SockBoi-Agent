"""SockBoi Agent HTTP API."""
from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import __version__
from .agents.planner import AssessmentPlan, build_plan
from .evidence import sha256_hex
from .knowledge import skill_library
from .models import (
    ActionRisk,
    Approval,
    AuditEvent,
    Engagement,
    EngagementCreate,
    Finding,
    FindingCreate,
)
from .policy import PolicyDenied, asset_matches, authorize_action
from .store import store
from .tool_registry import list_tools

app = FastAPI(
    title="SockBoi Agent",
    version=__version__,
    description="Modular Agent + Skills + MCP platform for authorized security assessments.",
)


class SkillIngestRequest(BaseModel):
    source: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)


class EvidenceHashRequest(BaseModel):
    content: str = Field(min_length=1, max_length=256000)


class ApprovalRequest(BaseModel):
    action: str = Field(min_length=3, max_length=120)
    target: str = Field(min_length=1, max_length=253)
    technique_id: str = Field(min_length=3, max_length=120)
    requested_by: str = Field(min_length=3, max_length=254)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "sockboi-agent", "version": __version__}


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


@app.post("/engagements/{engagement_id}/plan", response_model=AssessmentPlan)
def create_agent_plan(engagement_id: UUID, target: str) -> AssessmentPlan:
    engagement = store.engagements.get(engagement_id)
    if engagement is None:
        raise HTTPException(404, "engagement not found")
    try:
        plan = build_plan(engagement, target)
    except ValueError as exc:
        store.log(AuditEvent(
            engagement_id=engagement_id, event_type="agent.plan.denied",
            actor="api", detail={"target": target, "reason": str(exc)},
        ))
        raise HTTPException(403, str(exc)) from exc
    store.log(AuditEvent(
        engagement_id=engagement_id, event_type="agent.plan.created",
        actor="api", detail={"plan_id": str(plan.plan_id), "target": target,
                             "steps": len(plan.steps)},
    ))
    return plan


@app.post("/engagements/{engagement_id}/approvals", response_model=Approval, status_code=201)
def request_approval(engagement_id: UUID, payload: ApprovalRequest) -> Approval:
    engagement = store.engagements.get(engagement_id)
    if engagement is None:
        raise HTTPException(404, "engagement not found")
    if not any(asset_matches(asset, payload.target) for asset in engagement.scope):
        raise HTTPException(403, "approval target must be in engagement scope")
    item = Approval(
        engagement_id=engagement_id, action=payload.action, target=payload.target,
        technique_id=payload.technique_id, requested_by=payload.requested_by,
    )
    store.approvals[item.id] = item
    store.log(AuditEvent(
        engagement_id=engagement_id, event_type="approval.requested",
        actor=payload.requested_by,
        detail={"approval_id": str(item.id), "target": payload.target,
                "technique_id": payload.technique_id},
    ))
    return item


@app.post("/approvals/{approval_id}/decide", response_model=Approval)
def decide_approval(approval_id: UUID, approved_by: str, approved: bool) -> Approval:
    item = store.approvals.get(approval_id)
    if item is None:
        raise HTTPException(404, "approval not found")
    if approved and approved_by == item.requested_by:
        raise HTTPException(403, "requester cannot approve their own request")
    item.approved = approved
    item.approved_by = approved_by
    store.log(AuditEvent(
        engagement_id=item.engagement_id, event_type="approval.decided",
        actor=approved_by, detail={"approval_id": str(item.id), "approved": approved},
    ))
    return item


@app.post("/policy/check")
def policy_check(
    engagement_id: UUID, target: str, risk: ActionRisk,
    technique_id: str | None = None, approval_id: UUID | None = None,
) -> dict:
    engagement = store.engagements.get(engagement_id)
    if engagement is None:
        raise HTTPException(404, "engagement not found")
    approval = store.approvals.get(approval_id) if approval_id else None
    try:
        authorize_action(engagement, target, risk, approval, technique_id)
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
    if not any(asset_matches(asset, payload.asset) for asset in engagement.scope):
        raise HTTPException(403, "finding asset must be within an explicitly scoped asset")
    finding = Finding(**payload.model_dump())
    store.findings[finding.id] = finding
    store.log(AuditEvent(
        engagement_id=engagement.id, event_type="finding.created",
        actor="api", detail={"finding_id": str(finding.id), "severity": finding.severity},
    ))
    return finding


@app.post("/knowledge/ingest")
def ingest_knowledge(payload: SkillIngestRequest) -> dict:
    try:
        document = skill_library.ingest_markdown(payload.source, payload.content)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "document_id": document.document_id, "title": document.title,
        "source": document.source, "content_sha256": document.content_sha256,
        "trust": "untrusted_reference", "execution_enabled": False,
    }


@app.get("/knowledge/search")
def search_knowledge(query: str, limit: int = 5) -> dict:
    return {"results": skill_library.search(query, limit)}


@app.get("/tools")
def get_tool_catalog() -> dict:
    return {"tools": list_tools(), "execution_enabled": False}


@app.post("/evidence/hash")
def hash_evidence(payload: EvidenceHashRequest) -> dict:
    return {"algorithm": "SHA-256", "sha256": sha256_hex(payload.content),
            "stored": False, "note": "Only a digest is returned; evidence content is not persisted."}


@app.get("/engagements/{engagement_id}/audit", response_model=list[AuditEvent])
def get_audit(engagement_id: UUID) -> list[AuditEvent]:
    if engagement_id not in store.engagements:
        raise HTTPException(404, "engagement not found")
    return [event for event in store.audit if event.engagement_id == engagement_id]
