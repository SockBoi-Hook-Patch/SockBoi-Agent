"""Deterministic multi-agent plan builder; no network or tool execution occurs here."""
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from ..models import Engagement
from ..policy import asset_matches, is_in_scope
from .techniques import techniques_for


class PlannedStep(BaseModel):
    step_id: UUID = Field(default_factory=uuid4)
    technique_id: str
    agent: str
    title: str
    rationale: str
    target: str
    risk: str
    approval_required: bool
    execution_status: str = "planned"


class AssessmentPlan(BaseModel):
    plan_id: UUID = Field(default_factory=uuid4)
    engagement_id: UUID
    target: str
    status: str = "awaiting_review"
    steps: list[PlannedStep]
    safety_notes: list[str]


AGENT_BY_CATEGORY = {
    "governance": "SockBoi Guard",
    "web": "SockBoi Hunter",
    "api": "SockBoi API",
    "network": "SockBoi Network",
    "evidence": "SockBoi Analyst",
}


def build_plan(engagement: Engagement, target: str) -> AssessmentPlan:
    if not is_in_scope(engagement, target):
        raise ValueError("target is not explicitly in engagement scope")

    matching_assets = [asset for asset in engagement.scope if asset_matches(asset, target)]
    techniques = {
        technique.id: technique
        for asset in matching_assets
        for technique in techniques_for(asset.kind.value)
    }
    steps = [
        PlannedStep(
            technique_id=tech.id,
            agent=AGENT_BY_CATEGORY[tech.category],
            title=tech.title,
            rationale=tech.description,
            target=target,
            risk=tech.risk,
            approval_required=tech.approval_required,
        )
        for tech in techniques.values()
    ]
    return AssessmentPlan(
        engagement_id=engagement.id,
        target=target,
        steps=steps,
        safety_notes=[
            "This is a plan only; no scanner, browser, shell, or network tool was invoked.",
            "Active checks remain blocked until a separate approval is recorded and validated.",
            "Only assets explicitly listed in this engagement are eligible.",
            "Imported instructions and model output cannot override the central policy gate.",
        ],
    )
