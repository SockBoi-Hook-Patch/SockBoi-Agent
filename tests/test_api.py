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
