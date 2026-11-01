from hashlib import sha256

import pytest
from fastapi.testclient import TestClient

from sockboi.evidence import sha256_hex
from sockboi.knowledge import SkillLibrary
from sockboi.main import app
from sockboi.models import ActionRisk, Approval, Engagement, ScopeAsset
from sockboi.policy import PolicyDenied, authorize_action
from sockboi.store import store
from sockboi.tool_registry import list_tools

client = TestClient(app)


def setup_function():
    store.engagements.clear()
    store.approvals.clear()
    store.findings.clear()
    store.audit.clear()


def test_skill_ingestion_and_retrieval_is_untrusted():
    library = SkillLibrary()
    doc = library.ingest_markdown("repo/skill.md", "# Header review\nCheck CSP headers")
    assert doc.trusted_for_execution is False
    assert library.search("CSP")[0]["document_id"] == doc.document_id
    with pytest.raises(ValueError):
        library.ingest_markdown("empty.md", " ")


def test_evidence_hash_is_sha256():
    assert sha256_hex("proof") == sha256(b"proof").hexdigest()


def test_tool_registry_has_no_enabled_execution():
    tools = list_tools()
    assert tools
    assert all(tool["execution_enabled"] is False for tool in tools)


def test_approval_is_bound_to_target_and_technique_and_separate_actor():
    engagement = Engagement(
        name="Authorized lab", authorization_ref="ROE-001",
        owner="owner@example.org",
        scope=[ScopeAsset(kind="domain", value="lab.example.org")],
    )
    approval = Approval(
        engagement_id=engagement.id, action="safe_check",
        target="lab.example.org", technique_id="web.headers_review",
        requested_by="requester", approved_by="reviewer", approved=True,
    )
    authorize_action(
        engagement, "lab.example.org", ActionRisk.ACTIVE,
        approval, "web.headers_review",
    )
    with pytest.raises(PolicyDenied, match="different target"):
        authorize_action(
            engagement, "other.lab.example.org", ActionRisk.ACTIVE,
            approval, "web.headers_review",
        )
    with pytest.raises(PolicyDenied, match="different technique"):
        authorize_action(
            engagement, "lab.example.org", ActionRisk.ACTIVE,
            approval, "web.tls_review",
        )


def test_self_approval_rejected():
    engagement = Engagement(
        name="Authorized lab", authorization_ref="ROE-001",
        owner="owner@example.org",
        scope=[ScopeAsset(kind="domain", value="lab.example.org")],
    )
    approval = Approval(
        engagement_id=engagement.id, action="safe_check",
        target="lab.example.org", technique_id="web.headers_review",
        requested_by="same-user", approved_by="same-user", approved=True,
    )
    with pytest.raises(PolicyDenied, match="cannot approve"):
        authorize_action(
            engagement, "lab.example.org", ActionRisk.ACTIVE,
            approval, "web.headers_review",
        )


def test_api_exposes_v03_capabilities():
    assert client.get("/health").json()["version"] == "0.3.0"
    assert client.get("/tools").json()["execution_enabled"] is False
    ingested = client.post("/knowledge/ingest", json={
        "source": "local/hackskill.md", "content": "# Test skill\nHTTP header review"
    })
    assert ingested.status_code == 200
    assert ingested.json()["trust"] == "untrusted_reference"
    assert client.get("/knowledge/search", params={"query": "header"}).json()["results"]
    assert client.post("/evidence/hash", json={"content": "abc"}).json()["sha256"] == sha256(b"abc").hexdigest()


def test_approval_api_rejects_self_approval():
    created = client.post("/engagements", json={
        "name": "Authorized lab", "authorization_ref": "ROE-001",
        "owner": "owner@example.org",
        "scope": [{"kind": "domain", "value": "lab.example.org"}],
    })
    eid = created.json()["id"]
    requested = client.post(f"/engagements/{eid}/approvals", json={
        "action": "safe_check", "target": "lab.example.org",
        "technique_id": "web.headers_review", "requested_by": "alice",
    })
    assert requested.status_code == 201
    denied = client.post(
        f"/approvals/{requested.json()['id']}/decide",
        params={"approved_by": "alice", "approved": "true"},
    )
    assert denied.status_code == 403
