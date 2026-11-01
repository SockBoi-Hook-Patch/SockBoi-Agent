"""Safe, offline APK container triage.

This module never extracts or executes APK contents. It inventories bounded ZIP
metadata and a small number of explicitly selected headers.
"""
from __future__ import annotations

import hashlib
import io
import re
import stat
import struct
import zipfile
from pathlib import PurePosixPath
from xml.etree import ElementTree

MAX_APK_BYTES = 100 * 1024 * 1024
MAX_ENTRIES = 20_000
MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024
MAX_ENTRY_BYTES = 128 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200
MAX_MANIFEST_BYTES = 4 * 1024 * 1024
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


class ApkInspectionError(ValueError):
    """Raised when an APK violates bounded offline inspection rules."""


def _safe_member_name(name: str) -> str:
    if not name or "\\" in name or name.startswith("/"):
        raise ApkInspectionError("unsafe archive member path")
    path = PurePosixPath(name)
    if any(part in ("", ".", "..") for part in path.parts):
        raise ApkInspectionError("unsafe archive member path")
    if path.is_absolute():
        raise ApkInspectionError("absolute archive member path")
    return str(path)


def _elf_metadata(header: bytes) -> dict | None:
    if len(header) < 20 or header[:4] != b"\x7fELF":
        return None
    elf_class = {1: "ELF32", 2: "ELF64"}.get(header[4], "unknown")
    endian = {1: "<", 2: ">"}.get(header[5])
    if endian is None:
        return {"class": elf_class, "endianness": "unknown", "machine": None}
    machine = struct.unpack(endian + "H", header[18:20])[0]
    machines = {3: "x86", 40: "ARM", 62: "x86_64", 183: "AArch64", 243: "RISC-V"}
    return {
        "class": elf_class,
        "endianness": "little" if endian == "<" else "big",
        "machine": machines.get(machine, f"unknown:{machine}"),
    }


def _manifest_summary(archive: zipfile.ZipFile, names: set[str]) -> dict:
    if "AndroidManifest.xml" not in names:
        return {"status": "missing"}
    info = archive.getinfo("AndroidManifest.xml")
    if info.file_size > MAX_MANIFEST_BYTES:
        return {"status": "too_large", "size": info.file_size}
    raw = archive.read("AndroidManifest.xml")
    if raw.lstrip().startswith(b"<"):
        try:
            root = ElementTree.fromstring(raw)
        except ElementTree.ParseError:
            return {"status": "invalid_xml"}
        app = root.find("application")
        components = []
        if app is not None:
            for tag in ("activity", "activity-alias", "service", "receiver", "provider"):
                for item in app.findall(tag):
                    components.append({
                        "type": tag,
                        "name": item.get(ANDROID_NS + "name"),
                        "exported": item.get(ANDROID_NS + "exported"),
                        "permission": item.get(ANDROID_NS + "permission"),
                        "has_intent_filter": item.find("intent-filter") is not None,
                    })
        permissions = sorted({
            item.get(ANDROID_NS + "name")
            for item in root.findall("uses-permission")
            if item.get(ANDROID_NS + "name")
        })
        return {
            "status": "parsed_text_xml",
            "package": root.get("package"),
            "permissions": permissions,
            "application": {
                "debuggable": app.get(ANDROID_NS + "debuggable") if app is not None else None,
                "allow_backup": app.get(ANDROID_NS + "allowBackup") if app is not None else None,
                "uses_cleartext_traffic": (
                    app.get(ANDROID_NS + "usesCleartextTraffic") if app is not None else None
                ),
            },
            "components": components,
        }
    return {
        "status": "binary_android_xml",
        "note": "Use a separately sandboxed Apktool/aapt adapter for decoded manifest fields.",
    }


def inspect_apk_bytes(data: bytes, *, max_bytes: int = MAX_APK_BYTES) -> dict:
    """Return bounded static APK inventory and SHA-256 without extraction/execution."""
    if not isinstance(data, bytes):
        raise TypeError("APK input must be bytes")
    if not data:
        raise ApkInspectionError("APK is empty")
    if len(data) > max_bytes:
        raise ApkInspectionError("APK exceeds configured size limit")
    if not data.startswith(b"PK"):
        raise ApkInspectionError("input is not a ZIP-based APK")

    digest = hashlib.sha256(data).hexdigest()
    try:
        archive = zipfile.ZipFile(io.BytesIO(data), "r")
    except (zipfile.BadZipFile, OSError) as exc:
        raise ApkInspectionError("invalid APK ZIP container") from exc

    with archive:
        infos = archive.infolist()
        if len(infos) > MAX_ENTRIES:
            raise ApkInspectionError("APK contains too many archive entries")

        names: set[str] = set()
        total_uncompressed = 0
        dex_files = []
        native_libraries = []
        resource_files = 0
        asset_files = 0
        v1_signature_entries = []
        for info in infos:
            name = _safe_member_name(info.filename.rstrip("/")) if info.filename.rstrip("/") else ""
            if not name:
                continue
            if name in names:
                raise ApkInspectionError("duplicate archive member path")
            names.add(name)
            if info.flag_bits & 0x1:
                raise ApkInspectionError("encrypted archive members are not supported")
            if info.file_size > MAX_ENTRY_BYTES:
                raise ApkInspectionError("archive member exceeds size limit")
            total_uncompressed += info.file_size
            if total_uncompressed > MAX_UNCOMPRESSED_BYTES:
                raise ApkInspectionError("APK exceeds total uncompressed size limit")
            if info.file_size and info.compress_size == 0:
                raise ApkInspectionError("invalid compression metadata")
            if info.compress_size and info.file_size / info.compress_size > MAX_COMPRESSION_RATIO:
                raise ApkInspectionError("archive member compression ratio exceeds limit")
            unix_mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(unix_mode):
                raise ApkInspectionError("symbolic links are not allowed in APK archive")
            if info.is_dir():
                continue
            if re.fullmatch(r"classes(?:\d+)?\.dex", name):
                dex_files.append({"path": name, "size": info.file_size})
            if name.startswith("lib/") and name.endswith(".so"):
                abi = name.split("/", 2)[1] if len(name.split("/")) > 2 else "unknown"
                with archive.open(info) as member:
                    header = member.read(20)
                native_libraries.append({
                    "path": name, "abi": abi, "size": info.file_size,
                    "elf": _elf_metadata(header),
                })
            if name.startswith("res/"):
                resource_files += 1
            if name.startswith("assets/"):
                asset_files += 1
            upper = name.upper()
            if upper.startswith("META-INF/") and upper.endswith((".RSA", ".DSA", ".EC")):
                v1_signature_entries.append(name)

        dex_files.sort(key=lambda item: item["path"])
        native_libraries.sort(key=lambda item: item["path"])
        return {
            "format": "android-apk-zip",
            "sha256": digest,
            "size_bytes": len(data),
            "entry_count": len(infos),
            "uncompressed_size_bytes": total_uncompressed,
            "package_manifest": _manifest_summary(archive, names),
            "dex_files": dex_files,
            "native_libraries": native_libraries,
            "resource_file_count": resource_files,
            "asset_file_count": asset_files,
            "signing": {
                "v1_signature_entries": sorted(v1_signature_entries),
                "cryptographic_validity": "not_verified",
                "v2_v3_v4_status": "not_inspected",
            },
            "execution_performed": False,
            "files_extracted": False,
            "limitations": [
                "Binary AndroidManifest.xml requires a dedicated decoder.",
                "APK signing entries are inventoried but signature validity is not verified.",
                "DEX and ELF files are inventoried by container metadata; code is not decompiled.",
            ],
        }
