import json
from datetime import UTC, datetime, timedelta

import pytest

from sockboi.approval import ActionEnvelope, ApprovalGrant, validate_approval
from sockboi.audit import append_event, verify_chain
from sockboi.security import (
    authenticate_api_key,
    key_record,
    load_keyring,
    require_role,
    require_tenant,



def test_api_key_authentication_and_authorization():
    record = key_record("secret-token", "alice", "tenant-a", ["operator"])
    principal = authenticate_api_key("secret-token", load_keyring(json.dumps([record])))
    assert principal.subject == "alice"
    assert principal.tenant_id == "tenant-a"
    require_role(principal, "operator")
    require_tenant(principal, "tenant-a")
    with pytest.raises(PermissionError):
        authenticate_api_key("wrong-token", load_keyring(json.dumps([record])))
    with pytest.raises(PermissionError):
        require_role(principal, "admin")
    with pytest.raises(PermissionError):
        require_tenant(principal, "tenant-b")


def test_keyring_rejects_malformed_records():
    with pytest.raises(ValueError):
        load_keyring("not-json")
    with pytest.raises(ValueError):
        load_keyring(json.dumps([{"key_sha256": "short"}]))


def test_approval_binds_entire_action_envelope():
    action = ActionEnvelope("eng-1", "tenant-a", "https://lab.example.test",
                            "http.inspect", "headers.get",
                            {"timeout": 3, "max_bytes": 4096}, "active")
    grant = ApprovalGrant(action.digest(), "alice", "bob",
                          datetime.now(UTC) + timedelta(minutes=5), "apr-1")
    validate_approval(action, grant)
    changed = ActionEnvelope("eng-1", "tenant-a", "https://lab.example.test",
                             "http.inspect", "headers.get",
                             {"timeout": 30, "max_bytes": 4096}, "active")
    with pytest.raises(PermissionError, match="does not match"):
        validate_approval(changed, grant)


def test_approval_rejects_expired_revoked_consumed_and_self_approval():
    action = ActionEnvelope("e", "t", "lab", "adapter", "check", {}, "active")
    now = datetime.now(UTC)
    with pytest.raises(PermissionError, match="expired"):
        validate_approval(action, ApprovalGrant(action.digest(), "a", "b",
                          now - timedelta(seconds=1), "id"), now)
    with pytest.raises(PermissionError, match="revoked"):
        validate_approval(action, ApprovalGrant(action.digest(), "a", "b",
                          now + timedelta(minutes=1), "id", revoked=True), now)
    with pytest.raises(PermissionError, match="consumed"):
        validate_approval(action, ApprovalGrant(action.digest(), "a", "b",
                          now + timedelta(minutes=1), "id", consumed=True), now)
    with pytest.raises(PermissionError, match="different actors"):
        validate_approval(action, ApprovalGrant(action.digest(), "a", "a",
                          now + timedelta(minutes=1), "id"), now)


def test_audit_chain_detects_tampering():
    events = []
    append_event(events, {"type": "approval.requested", "actor": "alice"})
    append_event(events, {"type": "approval.approved", "actor": "bob"})
    assert verify_chain(events)
    first = events[0]
    events[0] = type(first)(first.sequence, {"type": "tampered"},
                            first.previous_hash, first.event_hash)
    assert not verify_chain(events)
