import pytest

from sockboi.agents.planner import build_plan
from sockboi.models import Engagement, ScopeAsset


def make_engagement():
    return Engagement(
        name="Authorized lab review", authorization_ref="ROE-LAB-01",
        owner="owner@example.org",
        scope=[ScopeAsset(kind="domain", value="lab.example.org")],
    )


def test_plan_contains_passive_and_approval_gated_steps():
    plan = build_plan(make_engagement(), "lab.example.org")
    assert plan.status == "awaiting_review"
    assert plan.steps
    assert all(step.execution_status == "planned" for step in plan.steps)
    assert any(not step.approval_required for step in plan.steps)
    assert any(step.approval_required for step in plan.steps)


def test_out_of_scope_target_rejected():
    with pytest.raises(ValueError, match="not explicitly in engagement scope"):
        build_plan(make_engagement(), "outside.example.net")
