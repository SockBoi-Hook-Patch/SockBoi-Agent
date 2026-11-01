"""SockBoi Agent HTTP API."""
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from . import __version__
from .agents.planner import AssessmentPlan, build_plan
from .apk_inspector import MAX_APK_BYTES, ApkInspectionError, inspect_apk_bytes
from .approval import ActionEnvelope
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
from .security import authenticate_api_key, load_keyring, require_role, require_tenant
from .store import store
from .tool_registry import list_tools

app = FastAPI(
    title="SockBoi Agent", version=__version__,
    description="Modular Agent + Skills + MCP platform for authorized security assessments.",
)


@app.middleware("http")
async def require_api_identity(request: Request, call_next):
    """Fail-closed authentication for every API route except the liveness endpoint."""
    if request.url.path == "/health" or request.method == "OPTIONS":
        return await call_next(request)
    try:
        keyring = load_keyring()
    except (TypeError, ValueError):
        return JSONResponse(status_code=503, content={"detail": "API key configuration is invalid"})
    if not keyring:
        return JSONResponse(status_code=503, content={"detail": "API authentication is not configured"})
    authorization = request.headers.get("authorization", "")
    scheme, _, credential = authorization.partition(" ")
    if scheme.lower() != "bearer" or not credential:
        return JSONResponse(status_code=401, content={"detail": "Bearer API key required"})
    try:
        request.state.principal = authenticate_api_key(credential, keyring)
    except PermissionError:
        return JSONResponse(status_code=401, content={"detail": "Invalid API key"})
    return await call_next(request)


class SkillIngestRequest(BaseModel):
    source: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)


class EvidenceHashRequest(BaseModel):
    content: str = Field(min_length=1, max_length=256000)


class ApprovalRequest(BaseModel):
    action: str = Field(min_length=3, max_length=120)
    target: str = Field(min_length=1, max_length=253)
    technique_id: str = Field(min_length=3, max_length=120)
    adapter_id: str = Field(default="http.inspect", min_length=3, max_length=120)
    parameters: dict = Field(default_factory=dict)
    risk: ActionRisk = ActionRisk.ACTIVE


class ActionEnvelopeRequest(BaseModel):
    target: str = Field(min_length=1, max_length=253)
    technique_id: str = Field(min_length=3, max_length=120)
    adapter_id: str = Field(default="http.inspect", min_length=3, max_length=120)
    parameters: dict = Field(default_factory=dict)
    risk: ActionRisk = ActionRisk.ACTIVE


def _principal(request: Request):
    return request.state.principal


def _require_role(request: Request, *roles: str) -> None:
    try:
        require_role(_principal(request), *roles)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc


def _get_engagement(engagement_id: UUID, request: Request) -> Engagement:
    item = store.engagements.get(engagement_id)
    if item is None:
        raise HTTPException(404, "engagement not found")
    try:
        require_tenant(_principal(request), item.tenant_id)
    except PermissionError as exc:
        raise HTTPException(404, "engagement not found") from exc
    return item


def _action_envelope(engagement: Engagement, target: str, adapter_id: str,
                     technique_id: str, parameters: dict, risk: ActionRisk) -> ActionEnvelope:
    return ActionEnvelope(
        engagement_id=str(engagement.id), tenant_id=engagement.tenant_id, target=target,
        adapter_id=adapter_id, technique_id=technique_id, parameters=parameters, risk=risk.value,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "sockboi-agent", "version": __version__}


@app.post("/engagements", response_model=Engagement, status_code=201)
def create_engagement(payload: EngagementCreate, request: Request) -> Engagement:
    _require_role(request, "admin", "operator")
    data = payload.model_dump()
    data["owner"] = _principal(request).subject
    engagement = Engagement(**data, tenant_id=_principal(request).tenant_id)
    store.engagements[engagement.id] = engagement
    store.log(AuditEvent(
        engagement_id=engagement.id, event_type="engagement.created", actor=engagement.owner,
        detail={"authorization_ref": engagement.authorization_ref},
    ))
    return engagement


@app.get("/engagements", response_model=list[Engagement])
def list_engagements(request: Request) -> list[Engagement]:
    tenant_id = _principal(request).tenant_id
    return [item for item in store.engagements.values() if item.tenant_id == tenant_id]


@app.get("/engagements/{engagement_id}", response_model=Engagement)
def get_engagement(engagement_id: UUID, request: Request) -> Engagement:
    return _get_engagement(engagement_id, request)


@app.post("/engagements/{engagement_id}/plan", response_model=AssessmentPlan)
def create_agent_plan(engagement_id: UUID, target: str, request: Request) -> AssessmentPlan:
    engagement = _get_engagement(engagement_id, request)
    try:
        plan = build_plan(engagement, target)
    except ValueError as exc:
        store.log(AuditEvent(
            engagement_id=engagement_id, event_type="agent.plan.denied",
            actor=_principal(request).subject, detail={"target": target, "reason": str(exc)},
        ))
        raise HTTPException(403, str(exc)) from exc
    store.log(AuditEvent(
        engagement_id=engagement_id, event_type="agent.plan.created",
        actor=_principal(request).subject,
        detail={"plan_id": str(plan.plan_id), "target": target, "steps": len(plan.steps)},
    ))
    return plan


@app.post("/engagements/{engagement_id}/approvals", response_model=Approval, status_code=201)
def request_approval(engagement_id: UUID, payload: ApprovalRequest, request: Request) -> Approval:
    _require_role(request, "admin", "operator")
    engagement = _get_engagement(engagement_id, request)
    if not any(asset_matches(asset, payload.target) for asset in engagement.scope):
        raise HTTPException(403, "approval target must be in engagement scope")
    envelope = _action_envelope(
        engagement, payload.target, payload.adapter_id, payload.technique_id,
        payload.parameters, payload.risk,
    )
    item = Approval(
        engagement_id=engagement_id, action=payload.action, target=payload.target,
        technique_id=payload.technique_id, adapter_id=payload.adapter_id,
        parameters=payload.parameters, risk=payload.risk, envelope_sha256=envelope.digest(),
        requested_by=_principal(request).subject,
    )
    store.approvals[item.id] = item
    store.log(AuditEvent(
        engagement_id=engagement_id, event_type="approval.requested",
        actor=_principal(request).subject,
        detail={"approval_id": str(item.id), "envelope_sha256": item.envelope_sha256,
                "target": payload.target, "technique_id": payload.technique_id},
    ))
    return item


@app.post("/approvals/{approval_id}/decide", response_model=Approval)
def decide_approval(approval_id: UUID, approved: bool, request: Request) -> Approval:
    _require_role(request, "admin", "reviewer")
    item = store.approvals.get(approval_id)
    if item is None:
        raise HTTPException(404, "approval not found")
    _get_engagement(item.engagement_id, request)
    approved_by = _principal(request).subject
    if approved and approved_by == item.requested_by:
        raise HTTPException(403, "requester cannot approve their own request")
    expires_at = datetime.now(UTC) + timedelta(minutes=15) if approved else None
    try:
        item = store.decide_approval(approval_id, approved, approved_by, expires_at)
    except PermissionError as exc:
        raise HTTPException(409, str(exc)) from exc
    store.log(AuditEvent(
        engagement_id=item.engagement_id, event_type="approval.decided", actor=approved_by,
        detail={"approval_id": str(item.id), "approved": approved,
                "expires_at": item.expires_at.isoformat() if item.expires_at else None},
    ))
    return item


@app.post("/approvals/{approval_id}/consume", response_model=Approval)
def consume_approval(approval_id: UUID, payload: ActionEnvelopeRequest,
                     engagement_id: UUID, request: Request) -> Approval:
    """Consume a one-time grant for an exact action; this endpoint does not execute network traffic."""
    _require_role(request, "admin", "operator")
    engagement = _get_engagement(engagement_id, request)
    item = store.approvals.get(approval_id)
    if item is None or item.engagement_id != engagement.id:
        raise HTTPException(404, "approval not found")
    envelope = _action_envelope(
        engagement, payload.target, payload.adapter_id, payload.technique_id,
        payload.parameters, payload.risk,
    )
    try:
        consumed = store.consume_approval(approval_id, envelope.digest(), _principal(request).subject)
    except PermissionError as exc:
        store.log(AuditEvent(
            engagement_id=engagement.id, event_type="approval.consume.denied",
            actor=_principal(request).subject,
            detail={"approval_id": str(approval_id), "reason": str(exc)},
        ))
        raise HTTPException(403, str(exc)) from exc
    store.log(AuditEvent(
        engagement_id=engagement.id, event_type="approval.consumed",
        actor=_principal(request).subject,
        detail={"approval_id": str(approval_id), "envelope_sha256": envelope.digest()},
    ))
    return consumed


@app.post("/policy/check")
def policy_check(
    engagement_id: UUID, target: str, risk: ActionRisk,
    request: Request, technique_id: str | None = None, approval_id: UUID | None = None,
) -> dict:
    engagement = _get_engagement(engagement_id, request)
    approval = store.approvals.get(approval_id) if approval_id else None
    try:
        authorize_action(engagement, target, risk, approval, technique_id)
    except PolicyDenied as exc:
        store.log(AuditEvent(
            engagement_id=engagement_id, event_type="policy.denied",
            actor=_principal(request).subject,
            detail={"target": target, "risk": risk.value, "reason": str(exc)},
        ))
        raise HTTPException(403, str(exc)) from exc
    store.log(AuditEvent(
        engagement_id=engagement_id, event_type="policy.allowed",
        actor=_principal(request).subject, detail={"target": target, "risk": risk.value},
    ))
    return {"allowed": True, "target": target, "risk": risk.value}


@app.post("/findings", response_model=Finding, status_code=201)
def create_finding(payload: FindingCreate, request: Request) -> Finding:
    _require_role(request, "admin", "operator")
    engagement = _get_engagement(payload.engagement_id, request)
    if not any(asset_matches(asset, payload.asset) for asset in engagement.scope):
        raise HTTPException(403, "finding asset must be within an explicitly scoped asset")
    finding = Finding(**payload.model_dump())
    store.findings[finding.id] = finding
    store.log(AuditEvent(
        engagement_id=engagement.id, event_type="finding.created",
        actor=_principal(request).subject,
        detail={"finding_id": str(finding.id), "severity": finding.severity},
    ))
    return finding


@app.post("/knowledge/ingest")
def ingest_knowledge(payload: SkillIngestRequest, request: Request) -> dict:
    _require_role(request, "admin", "operator")
    try:
        document = skill_library.ingest_markdown(
            payload.source, payload.content, tenant_id=_principal(request).tenant_id,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "document_id": document.document_id, "title": document.title,
        "source": document.source, "content_sha256": document.content_sha256,
        "trust": "untrusted_reference", "execution_enabled": False,
    }


@app.get("/knowledge/search")
def search_knowledge(query: str, request: Request, limit: int = 5) -> dict:
    return {
        "results": skill_library.search(
            query, limit, tenant_id=_principal(request).tenant_id,
        )
    }


@app.get("/tools")
def get_tool_catalog() -> dict:
    return {"tools": list_tools(), "execution_enabled": False}


@app.post("/evidence/hash")
def hash_evidence(payload: EvidenceHashRequest) -> dict:
    return {"algorithm": "SHA-256", "sha256": sha256_hex(payload.content),
            "stored": False, "note": "Only a digest is returned; evidence content is not persisted."}


@app.get("/engagements/{engagement_id}/audit", response_model=list[AuditEvent])
def get_audit(engagement_id: UUID, request: Request) -> list[AuditEvent]:
    _get_engagement(engagement_id, request)
    return [event for event in store.audit if event.engagement_id == engagement_id]


@app.get("/engagements/{engagement_id}/audit/verify")
def verify_audit_chain(engagement_id: UUID, request: Request) -> dict:
    """Verify this engagement's audit view without disclosing other engagements' metadata."""
    _require_role(request, "admin", "reviewer")
    _get_engagement(engagement_id, request)
    return store.verify_audit_chain(engagement_id)


@app.get("/engagements/{engagement_id}/audit/checkpoint")
def create_audit_checkpoint(engagement_id: UUID, request: Request) -> dict:
    """Create a signed checkpoint; callers must retain it outside this database."""
    _require_role(request, "admin", "reviewer")
    _get_engagement(engagement_id, request)
    try:
        return store.create_audit_checkpoint(engagement_id)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc


@app.post("/engagements/{engagement_id}/apk/inspect")
async def inspect_apk(
    engagement_id: UUID, request: Request, file: Annotated[UploadFile, File()]
) -> dict:
    """Inspect an uploaded APK as an untrusted ZIP; never extracts or executes it."""
    _require_role(request, "admin", "operator")
    _get_engagement(engagement_id, request)
    payload = bytearray()
    try:
        while chunk := await file.read(1024 * 1024):
            if len(payload) + len(chunk) > MAX_APK_BYTES:
                store.log(AuditEvent(
                    engagement_id=engagement_id, event_type="apk.inspect.rejected",
                    actor=_principal(request).subject,
                    detail={"reason": "size_limit", "limit_bytes": MAX_APK_BYTES},
                ))
                raise HTTPException(413, "APK exceeds configured upload size limit")
            payload.extend(chunk)
        try:
            result = inspect_apk_bytes(bytes(payload))
        except ApkInspectionError as exc:
            store.log(AuditEvent(
                engagement_id=engagement_id, event_type="apk.inspect.rejected",
                actor=_principal(request).subject,
                detail={"reason": str(exc)[:200]},
            ))
            raise HTTPException(400, str(exc)) from exc
        store.log(AuditEvent(
            engagement_id=engagement_id, event_type="apk.inspect.completed",
            actor=_principal(request).subject,
            detail={
                "artifact_sha256": result["sha256"],
                "size_bytes": result["size_bytes"],
                "entry_count": result["entry_count"],
                "manifest_status": result["package_manifest"]["status"],
                "dex_count": len(result["dex_files"]),
                "native_library_count": len(result["native_libraries"]),
            },
        ))
        return result
    finally:
        await file.close()
