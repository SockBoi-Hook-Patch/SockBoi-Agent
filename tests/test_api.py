from fastapi.testclient import TestClient

from sockboi.main import app
from sockboi.store import store

client = TestClient(app, headers={'Authorization': 'Bearer test-key'})


def setup_function():
    store.engagements.clear()
    store.approvals.clear()
    store.findings.clear()
    store.audit.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_engagement_and_policy_check():
    response = client.post("/engagements", json={
        "name": "Staging assessment",
        "authorization_ref": "ROE-2026-001",
        "owner": "security@example.org",
        "scope": [{"kind": "domain", "value": "staging.example.org"}],
    })
    assert response.status_code == 201
    engagement_id = response.json()["id"]
    allowed = client.post("/policy/check", params={
        "engagement_id": engagement_id,
        "target": "staging.example.org",
        "risk": "passive",
    })
    assert allowed.status_code == 200
    denied = client.post("/policy/check", params={
        "engagement_id": engagement_id,
        "target": "outside.example.net",
        "risk": "passive",
    })
    assert denied.status_code == 403


def test_api_requires_bearer_key_and_isolates_tenants():
    unauthenticated = TestClient(app)
    assert unauthenticated.get("/engagements").status_code == 401

    created = client.post("/engagements", json={
        "name": "Tenant A lab",
        "authorization_ref": "ROE-TENANT-A",
        "owner": "spoofed-owner@example.org",
        "scope": [{"kind": "domain", "value": "tenant-a.example.test"}],
    })
    assert created.status_code == 201
    assert created.json()["owner"] == "test-operator"
    assert created.json()["tenant_id"] == "test-tenant"

    tenant_b = TestClient(app, headers={"Authorization": "Bearer tenant-b-key"})
    assert tenant_b.get(f"/engagements/{created.json()['id']}").status_code == 404
    assert tenant_b.get("/engagements").json() == []

    denied = tenant_b.post("/engagements", json={
        "name": "Reader cannot create",
        "authorization_ref": "ROE-READER",
        "owner": "reader@example.org",
        "scope": [{"kind": "domain", "value": "reader.example.test"}],
    })
    assert denied.status_code == 403


def test_approval_is_bound_to_exact_action_and_consumed_once():
    created = client.post("/engagements", json={
        "name": "Approval binding lab",
        "authorization_ref": "ROE-APPROVAL-1",
        "owner": "ignored@example.org",
        "scope": [{"kind": "domain", "value": "approval.example.test"}],
    })
    assert created.status_code == 201
    engagement_id = created.json()["id"]
    requested = client.post(f"/engagements/{engagement_id}/approvals", json={
        "action": "inspect-http-security-headers",
        "target": "approval.example.test",
        "technique_id": "headers.get",
        "adapter_id": "http.inspect",
        "parameters": {"timeout": 3, "max_bytes": 4096},
        "risk": "active",
    })
    assert requested.status_code == 201
    approval_id = requested.json()["id"]

    reviewer = TestClient(app, headers={"Authorization": "Bearer reviewer-key"})
    decision = reviewer.post(f"/approvals/{approval_id}/decide", params={"approved": "true"})
    assert decision.status_code == 200
    assert decision.json()["expires_at"] is not None

    # A reviewer cannot rewrite a completed decision, even before consumption.
    second_decision = reviewer.post(
        f"/approvals/{approval_id}/decide", params={"approved": "false"}
    )
    assert second_decision.status_code == 409
    assert second_decision.json()["detail"] == "approval decision is immutable"

    changed_action = client.post(
        f"/approvals/{approval_id}/consume",
        params={"engagement_id": engagement_id},
        json={
            "target": "approval.example.test",
            "technique_id": "headers.get",
            "adapter_id": "http.inspect",
            "parameters": {"timeout": 30, "max_bytes": 4096},
            "risk": "active",
        },
    )
    assert changed_action.status_code == 403

    # Another operator in the same tenant cannot consume this requester's grant.
    peer_operator = TestClient(app, headers={"Authorization": "Bearer peer-operator-key"})
    delegated_consume = peer_operator.post(
        f"/approvals/{approval_id}/consume",
        params={"engagement_id": engagement_id},
        json={
            "target": "approval.example.test",
            "technique_id": "headers.get",
            "adapter_id": "http.inspect",
            "parameters": {"timeout": 3, "max_bytes": 4096},
            "risk": "active",
        },
    )
    assert delegated_consume.status_code == 403
    assert delegated_consume.json()["detail"] == (
        "only the original requester may consume this approval"
    )

    consumed = client.post(
        f"/approvals/{approval_id}/consume",
        params={"engagement_id": engagement_id},
        json={
            "target": "approval.example.test",
            "technique_id": "headers.get",
            "adapter_id": "http.inspect",
            "parameters": {"timeout": 3, "max_bytes": 4096},
            "risk": "active",
        },
    )
    assert consumed.status_code == 200
    assert consumed.json()["consumed"] is True

    replay = client.post(
        f"/approvals/{approval_id}/consume",
        params={"engagement_id": engagement_id},
        json={
            "target": "approval.example.test",
            "technique_id": "headers.get",
            "adapter_id": "http.inspect",
            "parameters": {"timeout": 3, "max_bytes": 4096},
            "risk": "active",
        },
    )
    assert replay.status_code == 403


def test_audit_chain_verification_endpoint_requires_reviewer():
    created = client.post("/engagements", json={
        "name": "Audit verification lab",
        "authorization_ref": "ROE-AUDIT-VERIFY",
        "owner": "ignored@example.org",
        "scope": [{"kind": "domain", "value": "audit.example.test"}],
    })
    assert created.status_code == 201
    engagement_id = created.json()["id"]

    reviewer = TestClient(app, headers={"Authorization": "Bearer reviewer-key"})
    verified = reviewer.get(f"/engagements/{engagement_id}/audit/verify")
    assert verified.status_code == 200
    assert verified.json()["valid"] is True
    assert verified.json()["event_count"] >= 1

    reader = TestClient(app, headers={"Authorization": "Bearer tenant-b-key"})
    forbidden = reader.get(f"/engagements/{engagement_id}/audit/verify")
    assert forbidden.status_code == 403
