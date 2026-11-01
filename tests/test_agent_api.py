from fastapi.testclient import TestClient
from sockboi.main import app
from sockboi.store import store

client = TestClient(app)


def setup_function():
    store.engagements.clear()
    store.approvals.clear()
    store.findings.clear()
    store.audit.clear()


def test_agent_plan_requires_scoped_target():
    created = client.post("/engagements", json={
        "name": "Authorized lab",
        "authorization_ref": "ROE-LAB-02",
        "owner": "tester@example.org",
        "scope": [{"kind": "domain", "value": "lab.example.org"}],
    })
    engagement_id = created.json()["id"]

    plan = client.post(
        f"/engagements/{engagement_id}/plan",
        params={"target": "lab.example.org"},
    )
    assert plan.status_code == 200
    body = plan.json()
    assert body["status"] == "awaiting_review"
    assert len(body["steps"]) > 0
    assert all(step["execution_status"] == "planned" for step in body["steps"])

    denied = client.post(
        f"/engagements/{engagement_id}/plan",
        params={"target": "outside.example.net"},
    )
    assert denied.status_code == 403
