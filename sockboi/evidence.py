"""Evidence integrity primitives; raw evidence is not persisted by this module."""
from hashlib import sha256


def sha256_hex(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()
