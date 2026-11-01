"""Append-only hash-chain helpers for tamper-evident audit streams."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class ChainedEvent:
    sequence: int
    payload: dict
    previous_hash: str
    event_hash: str


def event_hash(sequence: int, payload: dict, previous_hash: str) -> str:
    canonical = json.dumps(
        {"sequence": sequence, "payload": payload, "previous_hash": previous_hash},
        sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def append_event(events: list[ChainedEvent], payload: dict) -> ChainedEvent:
    previous = events[-1].event_hash if events else GENESIS_HASH
    item = ChainedEvent(len(events) + 1, payload, previous, event_hash(
        len(events) + 1, payload, previous
    ))
    events.append(item)
    return item


def verify_chain(events: list[ChainedEvent]) -> bool:
    previous = GENESIS_HASH
    for expected_sequence, item in enumerate(events, start=1):
        if item.sequence != expected_sequence or item.previous_hash != previous:
            return False
        if item.event_hash != event_hash(item.sequence, item.payload, item.previous_hash):
            return False
        previous = item.event_hash
    return True
