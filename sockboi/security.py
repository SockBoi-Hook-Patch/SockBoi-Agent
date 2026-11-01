"""Fail-closed API-key identity and tenant authorization primitives.

Keys are configured as SHA-256 digests in SOCKBOI_API_KEYS JSON. Raw API keys
must never be committed to source control or logged.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Principal:
    subject: str
    tenant_id: str
    roles: frozenset[str]


def _key_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_keyring(raw: str | None = None) -> dict[str, Principal]:
    """Load a digest-keyed keyring; malformed or empty configuration fails closed."""
    serialized = raw if raw is not None else os.getenv("SOCKBOI_API_KEYS", "")
    if not serialized:
        return {}
    try:
        records = json.loads(serialized)
    except json.JSONDecodeError as exc:
        raise ValueError("SOCKBOI_API_KEYS must be valid JSON") from exc
    if not isinstance(records, list):
        raise ValueError("SOCKBOI_API_KEYS must be a JSON array")
    keyring: dict[str, Principal] = {}
    for item in records:
        if not isinstance(item, dict):
            raise ValueError("each API key record must be an object")
        digest = item.get("key_sha256")
        subject = item.get("subject")
        tenant_id = item.get("tenant_id")
        roles = item.get("roles")
        if not all(isinstance(v, str) and v for v in (digest, subject, tenant_id)):
            raise ValueError("API key records require key_sha256, subject and tenant_id")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("key_sha256 must be a lowercase SHA-256 hex digest")
        if not isinstance(roles, list) or not roles or not all(
            isinstance(role, str) and role for role in roles
        ):
            raise ValueError("roles must be a non-empty string array")
        if digest in keyring:
            raise ValueError("duplicate API key digest")
        keyring[digest] = Principal(subject, tenant_id, frozenset(roles))
    return keyring


def authenticate_api_key(api_key: str, keyring: dict[str, Principal]) -> Principal:
    """Authenticate a presented API key without accepting caller-supplied identity."""
    if not api_key or len(api_key) > 4096:
        raise PermissionError("invalid API key")
    presented = _key_digest(api_key)
    for expected, principal in keyring.items():
        if hmac.compare_digest(presented, expected):
            return principal
    raise PermissionError("invalid API key")


def require_role(principal: Principal, *allowed_roles: str) -> None:
    if not principal.roles.intersection(allowed_roles):
        raise PermissionError("role is not permitted to perform this operation")


def require_tenant(principal: Principal, tenant_id: str) -> None:
    if not hmac.compare_digest(principal.tenant_id, tenant_id):
        raise PermissionError("resource belongs to a different tenant")


def key_record(api_key: str, subject: str, tenant_id: str, roles: Iterable[str]) -> dict:
    """Build a config record; call only in a trusted provisioning workflow."""
    if not api_key or not subject or not tenant_id:
        raise ValueError("api_key, subject and tenant_id are required")
    role_list = sorted(set(roles))
    if not role_list:
        raise ValueError("at least one role is required")
    return {
        "key_sha256": _key_digest(api_key),
        "subject": subject,
        "tenant_id": tenant_id,
        "roles": role_list,
    }
