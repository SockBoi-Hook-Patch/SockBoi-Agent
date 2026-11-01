import hashlib
import io
import zipfile

import pytest

from sockboi.apk_inspector import ApkInspectionError, inspect_apk_bytes


def make_apk(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in entries.items():
            archive.writestr(name, payload)
    return stream.getvalue()


def test_inspects_apk_without_extracting_and_hashes_content():
    manifest = b"""<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="org.example">
      <uses-permission android:name="android.permission.INTERNET"/>
      <application android:debuggable="false" android:allowBackup="false">
        <activity android:name=".Main" android:exported="true"><intent-filter/></activity>
      </application>
    </manifest>"""
    data = make_apk({
        "AndroidManifest.xml": manifest,
        "classes.dex": b"dex\n039\x00" + b"x" * 32,
        "lib/arm64-v8a/libsample.so": b"\x7fELF" + bytes([2, 1, 1, 0]) + b"\x00" * 10 + b"\xb7\x00",
        "res/values/strings.xml": b"<resources/>",
        "assets/config.json": b"{}",
    })
    result = inspect_apk_bytes(data)
    assert result["sha256"] == hashlib.sha256(data).hexdigest()
    assert result["package_manifest"]["package"] == "org.example"
    assert result["package_manifest"]["permissions"] == ["android.permission.INTERNET"]
    assert result["package_manifest"]["components"][0]["exported"] == "true"
    assert result["dex_files"][0]["path"] == "classes.dex"
    assert result["native_libraries"][0]["abi"] == "arm64-v8a"
    assert result["native_libraries"][0]["elf"]["machine"] == "AArch64"
    assert result["execution_performed"] is False
    assert result["files_extracted"] is False


def test_rejects_oversized_non_zip_and_corrupt_inputs():
    with pytest.raises(ApkInspectionError, match="size limit"):
        inspect_apk_bytes(b"PK" + b"x" * 20, max_bytes=10)
    with pytest.raises(ApkInspectionError, match="not a ZIP"):
        inspect_apk_bytes(b"not an apk")
    with pytest.raises(ApkInspectionError, match="invalid APK"):
        inspect_apk_bytes(b"PK-not-a-valid-zip")


def test_rejects_path_traversal_member():
    data = make_apk({"../escape.txt": b"bad"})
    with pytest.raises(ApkInspectionError, match="unsafe archive"):
        inspect_apk_bytes(data)


def test_rejects_compression_bomb_ratio():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("assets/repeat.txt", b"A" * 100_000)
    with pytest.raises(ApkInspectionError, match="compression ratio"):
        inspect_apk_bytes(stream.getvalue())


def test_binary_manifest_is_reported_as_unknown_not_guessed():
    result = inspect_apk_bytes(make_apk({
        "AndroidManifest.xml": b"\x03\x00\x08\x00binary-xml",
    }))
    assert result["package_manifest"]["status"] == "binary_android_xml"
    assert "package" not in result["package_manifest"]


def test_rejects_duplicate_paths():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("classes.dex", b"one")
        archive.writestr("classes.dex", b"two")
    with pytest.raises(ApkInspectionError, match="duplicate"):
        inspect_apk_bytes(stream.getvalue())
