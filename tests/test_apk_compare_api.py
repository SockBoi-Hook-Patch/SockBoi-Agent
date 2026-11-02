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


def make_apk(package: str, dex: bytes, extra: dict | None = None) -> bytes:
    stream = io.BytesIO()
    manifest = (
        f'<manifest package="{package}"><application/></manifest>'.encode()
    )
    entries = {"AndroidManifest.xml": manifest, "classes.dex": dex, **(extra or {})}
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    return stream.getvalue()


def create_engagement() -> str:
    response = client.post("/engagements", json={
        "name": "APK patch audit",
        "authorization_ref": "ROE-APK-PATCH-001",
        "owner": "ignored@example.org",
        "scope": [{"kind": "domain", "value": "mobile.example.test"}],
    })
    assert response.status_code == 201
    return response.json()["id"]


def test_apk_compare_endpoint_returns_offline_diff_and_audit_event():
    engagement_id = create_engagement()
    original = make_apk("org.example", b"dex-before")
    modified = make_apk(
        "org.example", b"dex-after",
        {"lib/arm64-v8a/libaudit.so": b"ELF-test"},
    )
    response = client.post(
        f"/engagements/{engagement_id}/apk/compare",
        files={
            "original_file": ("original.apk", original, "application/vnd.android.package-archive"),
            "modified_file": ("modified.apk", modified, "application/vnd.android.package-archive"),
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["package_identity_match"] is True
    assert body["change_count"] == 2
    assert body["signer_comparison"]["status"] == "not_verified"
    assert body["execution_performed"] is False
    assert body["source_artifacts_modified"] is False
    assert body["output_apk_created"] is False
    events = [event for event in store.audit if event.event_type == "apk.compare.completed"]
    assert len(events) == 1
    assert events[0].detail["original_sha256"] == body["original_sha256"]


def test_apk_compare_reports_package_identity_mismatch():
    engagement_id = create_engagement()
    response = client.post(
        f"/engagements/{engagement_id}/apk/compare",
        files={
            "original_file": ("original.apk", make_apk("org.before", b"dex"), "application/octet-stream"),
            "modified_file": ("modified.apk", make_apk("org.after", b"dex"), "application/octet-stream"),
        },
    )
    assert response.status_code == 200
    assert response.json()["package_identity_match"] is False


def test_apk_compare_rejects_cross_tenant_access():
    engagement_id = create_engagement()
    other_tenant = TestClient(app, headers={"Authorization": "Bearer tenant-b-operator-key"})
    response = other_tenant.post(
        f"/engagements/{engagement_id}/apk/compare",
        files={
            "original_file": ("original.apk", make_apk("org.example", b"dex"), "application/octet-stream"),
            "modified_file": ("modified.apk", make_apk("org.example", b"dex2"), "application/octet-stream"),
        },
    )
    assert response.status_code == 404


def test_apk_compare_rejects_non_apk_and_audits():
    engagement_id = create_engagement()
    response = client.post(
        f"/engagements/{engagement_id}/apk/compare",
        files={
            "original_file": ("original.apk", b"not apk", "application/octet-stream"),
            "modified_file": ("modified.apk", make_apk("org.example", b"dex"), "application/octet-stream"),
        },
    )
    assert response.status_code == 400
    assert any(event.event_type == "apk.compare.rejected" for event in store.audit)


def test_apk_compare_enforces_each_upload_size_limit(monkeypatch):
    engagement_id = create_engagement()
    monkeypatch.setattr("sockboi.main.MAX_APK_BYTES", 10)
    response = client.post(
        f"/engagements/{engagement_id}/apk/compare",
        files={
            "original_file": ("original.apk", b"PK" + b"x" * 20, "application/octet-stream"),
            "modified_file": ("modified.apk", make_apk("org.example", b"dex"), "application/octet-stream"),
        },
    )
    assert response.status_code == 413
