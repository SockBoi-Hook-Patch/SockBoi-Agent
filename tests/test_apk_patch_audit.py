import io
import zipfile

from sockboi.apk_patch_audit import compare_apk_bytes


def make_apk(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    return stream.getvalue()


def test_compares_apk_members_and_preserves_provenance():
    manifest = b'<manifest package="org.example"><application/></manifest>'
    original = make_apk({
        "AndroidManifest.xml": manifest,
        "classes.dex": b"dex-original",
        "assets/readme.txt": b"same",
    })
    modified = make_apk({
        "AndroidManifest.xml": manifest.replace(b"org.example", b"org.example"),
        "classes.dex": b"dex-modified",
        "assets/readme.txt": b"same",
        "lib/arm64-v8a/libaudit.so": b"ELF",
    })

    result = compare_apk_bytes(original, modified)

    assert result["evidence_type"] == "android.apk.patch_comparison"
    assert result["original_sha256"] != result["modified_sha256"]
    assert result["package_identity_match"] is True
    assert result["changed_entries"][0]["path"] == "classes.dex"
    assert result["added_entries"] == ["lib/arm64-v8a/libaudit.so"]
    assert result["security_relevant_changes"]
    assert result["signer_comparison"]["status"] == "not_verified"
    assert result["execution_performed"] is False
    assert result["source_artifacts_modified"] is False
    assert result["output_apk_created"] is False


def test_reports_package_identity_mismatch():
    original = make_apk({
        "AndroidManifest.xml": b'<manifest package="org.original"><application/></manifest>',
    })
    modified = make_apk({
        "AndroidManifest.xml": b'<manifest package="org.modified"><application/></manifest>',
    })
    result = compare_apk_bytes(original, modified)
    assert result["package_identity_match"] is False
    assert result["manifest_changed"] is True
