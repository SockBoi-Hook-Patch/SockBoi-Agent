import io
import zipfile

from fastapi.testclient import TestClient

from sockboi.main import app
from sockboi.store import store


client = TestClient(app, headers={"Authorization": "Bearer test-key"})


def setup_function():
    store.engagements.clear()
    store.approvals.clear()
    store.findings.clear()
    store.audit.clear()


def create_engagement():
    response = client.post("/engagements", json={
        "name": "APK assessment",
        "authorization_ref": "ROE-APK-001",
        "owner": "ignored@example.org",
        "scope": [{"kind": "domain", "value": "mobile.example.test"}],
    })
    assert response.status_code == 201
    return response.json()["id"]


def make_apk():
    stream = io.BytesIO()
    manifest = b"""<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.example">
      <uses-permission android:name="android.permission.INTERNET"/>
      <application android:debuggable="false"/>
    </manifest>"""
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("AndroidManifest.xml", manifest)
        archive.writestr("classes.dex", b"dex\n039\x00")
    return stream.getvalue()


def test_apk_inspection_endpoint_returns_static_inventory_and_audits():
    engagement_id = create_engagement()
    apk = make_apk()
    response = client.post(
        f"/engagements/{engagement_id}/apk/inspect",
        files={"file": ("target.apk", apk, "application/vnd.android.package-archive")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["package_manifest"]["package"] == "org.example"
    assert body["dex_files"][0]["path"] == "classes.dex"
    assert body["execution_performed"] is False
    events = [event for event in store.audit if event.event_type == "apk.inspect.completed"]
    assert len(events) == 1
    assert events[0].detail["artifact_sha256"] == body["sha256"]


def test_apk_inspection_rejects_non_apk_and_records_rejection():
    engagement_id = create_engagement()
    response = client.post(
        f"/engagements/{engagement_id}/apk/inspect",
        files={"file": ("not.apk", b"not an apk", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert any(event.event_type == "apk.inspect.rejected" for event in store.audit)


def test_apk_inspection_is_tenant_isolated():
    engagement_id = create_engagement()
    other_tenant = TestClient(app, headers={"Authorization": "Bearer tenant-b-operator-key"})
    response = other_tenant.post(
        f"/engagements/{engagement_id}/apk/inspect",
        files={"file": ("target.apk", make_apk(), "application/octet-stream")},
    )
    assert response.status_code == 404


def test_apk_inspection_enforces_upload_size_limit(monkeypatch):
    engagement_id = create_engagement()
    monkeypatch.setattr("sockboi.main.MAX_APK_BYTES", 10)
    response = client.post(
        f"/engagements/{engagement_id}/apk/inspect",
        files={"file": ("large.apk", b"PK" + b"x" * 20, "application/octet-stream")},
    )
    assert response.status_code == 413
