import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from sockboi.apk_patch_audit import ApkPatchAuditError, compare_apk_bytes
from sockboi.main import app
from sockboi.store import store


client = TestClient(app, headers={"Authorization": "Bearer test-key"})


def make_apk(dex: bytes, extra: dict[str, bytes] | None = None) -> bytes:
    stream = io.BytesIO()
    manifest = b"""<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.audit">
      <application android:debuggable="false"/>
    </manifest>"""
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("AndroidManifest.xml", manifest)
        archive.writestr("classes.dex", dex)
        for path, value in (extra or {}).items():
            archive.writestr(path, value)
    return stream.getvalue()


def test_patch_audit_reports_changed_added_and_removed_members():
    original = make_apk(b"original dex", {"assets/old.txt": b"old"})
    patched = make_apk(b"patched dex", {"assets/new.txt": b"new"})
    result = compare_apk_bytes(original, patched)

    assert result["package_identity"] == "same"
    assert result["summary"] == {
        "added_count": 1, "removed_count": 1, "changed_count": 1, "unchanged_count": 1,
    }
    changes = {(item["path"], item["change"]) for item in result["changes"]}
    assert ("classes.dex", "changed") in changes
    assert ("assets/new.txt", "added") in changes
    assert ("assets/old.txt", "removed") in changes
    assert result["apk_modified"] is False
    assert result["execution_performed"] is False


def test_patch_audit_rejects_invalid_input():
    with pytest.raises(ApkPatchAuditError):
        compare_apk_bytes(b"not apk", make_apk(b"dex"))


def setup_function():
    store.engagements.clear()
    store.approvals.clear()
    store.findings.clear()
    store.audit.clear()


def test_patch_audit_api_is_tenant_scoped_and_audited():
    engagement = client.post("/engagements", json={
        "name": "Patch review",
        "authorization_ref": "ROE-PATCH-001",
        "owner": "ignored",
        "scope": [{"kind": "domain", "value": "mobile.example.test"}],
    }).json()["id"]
    response = client.post(
        f"/engagements/{engagement}/apk/patch-audit",
        files={
            "original_file": ("original.apk", make_apk(b"before"), "application/octet-stream"),
            "patched_file": ("patched.apk", make_apk(b"after"), "application/octet-stream"),
        },
    )
    assert response.status_code == 200
    assert response.json()["summary"]["changed_count"] == 1
    assert any(event.event_type == "apk.patch_audit.completed" for event in store.audit)

    other_tenant = TestClient(app, headers={"Authorization": "Bearer tenant-b-operator-key"})
    denied = other_tenant.post(
        f"/engagements/{engagement}/apk/patch-audit",
        files={
            "original_file": ("original.apk", make_apk(b"before"), "application/octet-stream"),
            "patched_file": ("patched.apk", make_apk(b"after"), "application/octet-stream"),
        },
    )
    assert denied.status_code == 404
