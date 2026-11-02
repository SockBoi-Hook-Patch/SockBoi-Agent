"""Offline APK artifact comparison for authorized patch-integrity audits.

This module compares ZIP member digests and decoded metadata without extracting
files to disk, executing APK code, modifying either input, or producing a patched APK.
"""
from __future__ import annotations

import hashlib
import io
import zipfile

from .apk_inspector import ApkInspectionError, inspect_apk_bytes

MAX_DIFF_ITEMS = 2_000
CHUNK_SIZE = 1024 * 1024


def _member_digest(archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> str:
    digest = hashlib.sha256()
    with archive.open(info, "r") as member:
        while chunk := member.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _file_inventory(data: bytes) -> dict[str, tuple[int, str]]:
    inventory: dict[str, tuple[int, str]] = {}
    with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            inventory[info.filename] = (info.file_size, _member_digest(archive, info))
    return inventory


def _security_relevant(path: str) -> bool:
    lower = path.lower()
    return (
        path == "AndroidManifest.xml"
        or lower.endswith(".dex")
        or lower.startswith(("lib/", "meta-inf/", "res/xml/"))
        or "network_security_config" in lower
    )


def compare_apk_bytes(original: bytes, modified: bytes) -> dict:
    """Compare two bounded APKs and return a provenance-preserving static diff."""
    original_info = inspect_apk_bytes(original)
    modified_info = inspect_apk_bytes(modified)

    try:
        before = _file_inventory(original)
        after = _file_inventory(modified)
    except (zipfile.BadZipFile, RuntimeError, OSError) as exc:
        raise ApkInspectionError("APK member failed integrity check during comparison") from exc

    before_names = set(before)
    after_names = set(after)
    added_names = sorted(after_names - before_names)
    removed_names = sorted(before_names - after_names)
    common_names = before_names & after_names
    changed_names = sorted(
        name for name in common_names if before[name][1] != after[name][1]
    )

    all_changes = [
        {"path": name, "modified_size_bytes": after[name][0]}
        for name in added_names
    ] + [
        {"path": name, "original_size_bytes": before[name][0]}
        for name in removed_names
    ] + [
        {
            "path": name,
            "original_size_bytes": before[name][0],
            "modified_size_bytes": after[name][0],
            "original_member_sha256": before[name][1],
            "modified_member_sha256": after[name][1],
        }
        for name in changed_names
    ]
    all_changes.sort(key=lambda item: item["path"])
    security_changes = [
        item for item in all_changes if _security_relevant(item["path"])
    ]

    original_package = original_info["package_manifest"].get("package")
    modified_package = modified_info["package_manifest"].get("package")
    if original_package is None or modified_package is None:
        package_match = None
    else:
        package_match = original_package == modified_package

    manifest_changed = (
        before.get("AndroidManifest.xml", (None, None))[1]
        != after.get("AndroidManifest.xml", (None, None))[1]
    )
    return {
        "evidence_type": "android.apk.patch_comparison",
        "original_sha256": original_info["sha256"],
        "modified_sha256": modified_info["sha256"],
        "original_size_bytes": original_info["size_bytes"],
        "modified_size_bytes": modified_info["size_bytes"],
        "package_identity_match": package_match,
        "manifest_changed": manifest_changed,
        "original_manifest": original_info["package_manifest"],
        "modified_manifest": modified_info["package_manifest"],
        "added_entries": added_names[:MAX_DIFF_ITEMS],
        "removed_entries": removed_names[:MAX_DIFF_ITEMS],
        "changed_entries": [
            item for item in all_changes
            if item["path"] in set(changed_names)
        ][:MAX_DIFF_ITEMS],
        "security_relevant_changes": security_changes[:MAX_DIFF_ITEMS],
        "change_count": len(all_changes),
        "truncated": len(all_changes) > MAX_DIFF_ITEMS,
        "signer_comparison": {
            "status": "not_verified",
            "note": "ZIP signature-file presence is not cryptographic APK signer verification.",
        },
        "execution_performed": False,
        "files_extracted": False,
        "source_artifacts_modified": False,
        "output_apk_created": False,
        "limitations": [
            "Binary AndroidManifest.xml requires a dedicated decoder.",
            "DEX and native changes are identified by member digest, not decompiled semantics.",
            "Cryptographic APK signer verification requires a trusted platform verifier.",
            "This comparison does not create or modify APKs.",
        ],
    }
