import pytest

from sockboi.models import ActionRisk, Approval, Engagement, ScopeAsset
from sockboi.policy import PolicyDenied, authorize_action, is_in_scope


def engagement():
    return Engagement(
        name="Staging assessment",
        authorization_ref="ROE-123",
        owner="tester@example.org",
        scope=[ScopeAsset(kind="domain", value="staging.example.org"),
               ScopeAsset(kind="cidr", value="192.0.2.0/28")],
    )


def test_exact_domain_scope():
    item = engagement()
    assert is_in_scope(item, "staging.example.org")
    assert not is_in_scope(item, "admin.staging.example.org")
    assert not is_in_scope(item, "staging.example.org.attacker.invalid")


def test_cidr_scope():
    item = engagement()
    assert is_in_scope(item, "192.0.2.4")
    assert not is_in_scope(item, "192.0.2.30")


def test_passive_action_allowed_in_scope():
    authorize_action(engagement(), "staging.example.org", ActionRisk.PASSIVE)


def test_active_requires_approval():
    with pytest.raises(PolicyDenied):
        authorize_action(engagement(), "staging.example.org", ActionRisk.ACTIVE)


def test_approved_active_action_is_exactly_bound():
    item = engagement()
    approval = Approval(
        engagement_id=item.id, action="safe_validation",
        target="staging.example.org", technique_id="web.headers_review",
        requested_by="requester", approved_by="reviewer", approved=True,
    )
    authorize_action(
        item, "staging.example.org", ActionRisk.ACTIVE,
        approval, "web.headers_review",
    )


def test_wrong_engagement_approval_denied():
    item = engagement()
    other = engagement()
    approval = Approval(
        engagement_id=other.id, action="safe_validation",
        target="staging.example.org", technique_id="web.headers_review",
        requested_by="requester", approved_by="reviewer", approved=True,
    )
    with pytest.raises(PolicyDenied):
        authorize_action(
            item, "staging.example.org", ActionRisk.ACTIVE,
            approval, "web.headers_review",
        )
