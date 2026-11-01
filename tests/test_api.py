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
