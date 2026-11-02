"""Read-only comparison of two APK builds for patch audit.

This module does not modify, repackage, sign, install, or execute either APK.
It validates both containers with the existing bounded inspector, then hashes
members as streams to report added, removed, and changed archive entries.
"""
from __future__ import annotations

import hashlib
import io
import zipfile

from .apk_inspector import ApkInspectionError, inspect_apk_bytes


class ApkPatchAuditError(ValueError):
    """Raised when either APK cannot be safely compared."""


def _member_hashes(data: bytes) -> dict[str, dict[str, str | int]]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(data), "r")
    except (zipfile.BadZipFile, OSError) as exc:
        raise ApkPatchAuditError("invalid APK container during patch comparison") from exc

    members: dict[str, dict[str, str | int]] = {}
    with archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            digest = hashlib.sha256()
            size = 0
            try:
                with archive.open(info, "r") as stream:
                    while chunk := stream.read(1024 * 1024):
                        size += len(chunk)
                        digest.update(chunk)
            except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
                raise ApkPatchAuditError("APK member failed integrity check") from exc
            if size != info.file_size:
                raise ApkPatchAuditError("APK member size mismatch")
            members[info.filename] = {"sha256": digest.hexdigest(), "size_bytes": size}
    return members


def _category(path: str) -> str:
    upper = path.upper()
    if path == "AndroidManifest.xml":
        return "manifest"
    if path.endswith(".dex"):
        return "dex"
    if path.startswith("lib/") and path.endswith(".so"):
        return "native"
    if path.startswith("res/") or path == "resources.arsc":
        return "resources"
    if path.startswith("assets/"):
        return "assets"
    if upper.startswith("META-INF/") or path.startswith("BUNDLE-METADATA/"):
        return "signing-or-build-metadata"
    return "other"


def compare_apk_bytes(original: bytes, patched: bytes) -> dict:
    """Compare two APKs without extraction, mutation, or code execution."""
    try:
        original_info = inspect_apk_bytes(original)
        patched_info = inspect_apk_bytes(patched)
    except ApkInspectionError as exc:
        raise ApkPatchAuditError(str(exc)) from exc

    original_members = _member_hashes(original)
    patched_members = _member_hashes(patched)
    original_names = set(original_members)
    patched_names = set(patched_members)

    added = sorted(patched_names - original_names)
    removed = sorted(original_names - patched_names)
    changed = sorted(
        name for name in original_names & patched_names
        if original_members[name]["sha256"] != patched_members[name]["sha256"]
    )

    def describe(paths: list[str], kind: str) -> list[dict]:
        rows = []
        for path in paths:
            row = {"path": path, "category": _category(path), "change": kind}
            if path in original_members:
                row["original"] = original_members[path]
            if path in patched_members:
                row["patched"] = patched_members[path]
            rows.append(row)
        return rows

    original_package = original_info["package_manifest"].get("package")
    patched_package = patched_info["package_manifest"].get("package")
    package_status = "same" if original_package == patched_package else "changed_or_unknown"

    return {
        "format": "apk-patch-audit",
        "original": {
            "sha256": original_info["sha256"],
            "size_bytes": original_info["size_bytes"],
            "package": original_package,
        },
        "patched": {
            "sha256": patched_info["sha256"],
            "size_bytes": patched_info["size_bytes"],
            "package": patched_package,
        },
        "package_identity": package_status,
        "summary": {
            "added_count": len(added),
            "removed_count": len(removed),
            "changed_count": len(changed),
            "unchanged_count": len(original_names & patched_names) - len(changed),
        },
        "changes": (
            describe(added, "added")
            + describe(removed, "removed")
            + describe(changed, "changed")
        ),
        "signing_comparison": {
            "original_inventory": original_info["signing"],
            "patched_inventory": patched_info["signing"],
            "cryptographic_validity": "not_verified",
            "note": "A changed signing entry is not proof of valid or invalid APK signatures.",
        },
        "execution_performed": False,
        "files_extracted": False,
        "apk_modified": False,
        "limitations": [
            "This is a ZIP-member integrity comparison, not semantic DEX or native code analysis.",
            "Binary AndroidManifest.xml package identity may be unknown.",
            "APK cryptographic signature validity is not verified.",
            "No patch is applied and neither APK is installed or executed.",
        ],
    }
