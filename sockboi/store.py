"""SQLAlchemy-backed persistence for engagement, approval, finding and audit records."""
from __future__ import annotations

import hashlib
import hmac
import os
from collections.abc import Iterator, MutableMapping
from datetime import UTC, datetime
from threading import RLock
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

from .audit import GENESIS_HASH, ChainedEvent, event_hash, verify_chain
from .models import Approval, AuditEvent, Engagement, Finding


def _build_engine() -> Engine:
    url = os.getenv("SOCKBOI_DATABASE_URL", "sqlite:///./sockboi.db")
    options = {"pool_pre_ping": True, "future": True}
    if url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url:
            options["poolclass"] = StaticPool
    return create_engine(url, **options)


class DatabaseMapping[ModelT](MutableMapping[UUID, ModelT]):
    def __init__(self, engine: Engine, table: Table, model: type[ModelT], lock: RLock):
        self.engine, self.table, self.model, self.lock = engine, table, model, lock

    def __getitem__(self, key: UUID) -> ModelT:
        with self.engine.connect() as connection:
            payload = connection.execute(
                select(self.table.c.payload).where(self.table.c.id == str(key))
            ).scalar_one_or_none()
        if payload is None:
            raise KeyError(key)
        return self.model.model_validate_json(payload)

    def __setitem__(self, key: UUID, value: ModelT) -> None:
        payload = value.model_dump_json()
        with self.lock, self.engine.begin() as connection:
            connection.execute(delete(self.table).where(self.table.c.id == str(key)))
            connection.execute(insert(self.table).values(id=str(key), payload=payload))

    def __delitem__(self, key: UUID) -> None:
        with self.lock, self.engine.begin() as connection:
            result = connection.execute(delete(self.table).where(self.table.c.id == str(key)))
            if result.rowcount == 0:
                raise KeyError(key)

    def __iter__(self) -> Iterator[UUID]:
        with self.engine.connect() as connection:
            keys = connection.execute(select(self.table.c.id)).scalars().all()
        return iter(UUID(key) for key in keys)

    def __len__(self) -> int:
        with self.engine.connect() as connection:
            return len(connection.execute(select(self.table.c.id)).scalars().all())

    def values(self) -> list[ModelT]:
        with self.engine.connect() as connection:
            payloads = connection.execute(select(self.table.c.payload)).scalars().all()
        return [self.model.model_validate_json(payload) for payload in payloads]

    def clear(self) -> None:
        with self.lock, self.engine.begin() as connection:
            connection.execute(delete(self.table))


class AuditCollection:
    def __init__(self, engine: Engine, table: Table, chain_table: Table,
                 head_table: Table, lock: RLock):
        self.engine, self.table, self.chain_table = engine, table, chain_table
        self.head_table, self.lock = head_table, lock

    def append(self, event: AuditEvent) -> None:
        """Serialize writers across processes using a database-locked singleton head."""
        payload = event.model_dump(mode="json")
        with self.lock, self.engine.connect() as connection:
            try:
                if self.engine.dialect.name == "sqlite":
                    connection.exec_driver_sql("BEGIN IMMEDIATE")
                else:
                    connection.begin()
                head = connection.execute(
                    select(self.head_table.c.sequence, self.head_table.c.head_hash)
                    .where(self.head_table.c.id == 1).with_for_update()
                ).one()
                sequence = head.sequence + 1
                previous_hash = head.head_hash
                digest = event_hash(sequence, payload, previous_hash)
                connection.execute(insert(self.table).values(
                    event_id=str(event.id), engagement_id=str(event.engagement_id),
                    payload=event.model_dump_json(),
                ))
                connection.execute(insert(self.chain_table).values(
                    sequence=sequence, event_id=str(event.id),
                    engagement_id=str(event.engagement_id),
                    payload=event.model_dump_json(), previous_hash=previous_hash,
                    event_hash=digest,
                ))
                connection.execute(
                    update(self.head_table).where(self.head_table.c.id == 1).values(
                        sequence=sequence, head_hash=digest,
                    )
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise

    def verify(self) -> dict:
        """Verify sequence continuity, previous hashes and event digests."""
        with self.engine.connect() as connection:
            rows = connection.execute(
                select(self.chain_table.c.sequence, self.chain_table.c.payload,
                       self.chain_table.c.previous_hash, self.chain_table.c.event_hash)
                .order_by(self.chain_table.c.sequence)
            ).all()
        events = []
        try:
            for row in rows:
                events.append(ChainedEvent(
                    sequence=row.sequence,
                    payload=AuditEvent.model_validate_json(row.payload).model_dump(mode="json"),
                    previous_hash=row.previous_hash,
                    event_hash=row.event_hash,
                ))
        except (ValueError, ValidationError):
            return {
                "valid": False,
                "event_count": len(rows),
                "head_hash": rows[-1].event_hash if rows else GENESIS_HASH,
            }
        with self.engine.connect() as connection:
            head = connection.execute(
                select(self.head_table.c.sequence, self.head_table.c.head_hash)
                .where(self.head_table.c.id == 1)
            ).one()
        computed_hash = events[-1].event_hash if events else GENESIS_HASH
        head_matches = head.sequence == len(events) and head.head_hash == computed_hash
        return {
            "valid": verify_chain(events) and head_matches,
            "event_count": len(events),
            "head_hash": computed_hash,
            "head_matches": head_matches,
        }

    def __iter__(self) -> Iterator[AuditEvent]:
        with self.engine.connect() as connection:
            payloads = connection.execute(
                select(self.table.c.payload).order_by(self.table.c.sequence)
            ).scalars().all()
        return iter(AuditEvent.model_validate_json(payload) for payload in payloads)

    def clear(self) -> None:
        with self.lock, self.engine.begin() as connection:
            connection.execute(delete(self.table))
            connection.execute(delete(self.chain_table))
            connection.execute(
                update(self.head_table).where(self.head_table.c.id == 1).values(
                    sequence=0, head_hash=GENESIS_HASH,
                )
            )


class DatabaseStore:
    """Durable store; set SOCKBOI_DATABASE_URL to a PostgreSQL URL in deployments."""

    def __init__(self, database_url: str | None = None):
        self.engine = _build_engine() if database_url is None else create_engine(
            database_url, pool_pre_ping=True, future=True,
            **({"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
               if ":memory:" in database_url else {}),
        )
        self.lock = RLock()
        metadata = MetaData()
        self.engagement_table = Table(
            "engagements", metadata, Column("id", String(36), primary_key=True),
            Column("payload", Text, nullable=False),
        )
        self.approval_table = Table(
            "approvals", metadata, Column("id", String(36), primary_key=True),
            Column("payload", Text, nullable=False),
        )
        self.finding_table = Table(
            "findings", metadata, Column("id", String(36), primary_key=True),
            Column("payload", Text, nullable=False),
        )
        self.audit_table = Table(
            "audit_events", metadata, Column("sequence", Integer, primary_key=True, autoincrement=True),
            Column("event_id", String(36), unique=True, nullable=False),
            Column("engagement_id", String(36), nullable=False), Column("payload", Text, nullable=False),
        )
        self.audit_chain_table = Table(
            "audit_chain_events", metadata,
            Column("sequence", Integer, primary_key=True),
            Column("event_id", String(36), unique=True, nullable=False),
            Column("engagement_id", String(36), nullable=False),
            Column("payload", Text, nullable=False),
            Column("previous_hash", String(64), nullable=False),
            Column("event_hash", String(64), nullable=False),
        )
        self.audit_chain_head_table = Table(
            "audit_chain_head", metadata,
            Column("id", Integer, primary_key=True),
            Column("sequence", Integer, nullable=False),
            Column("head_hash", String(64), nullable=False),
        )
        metadata.create_all(self.engine)
        try:
            with self.engine.begin() as connection:
                last_event = connection.execute(
                    select(self.audit_chain_table.c.sequence, self.audit_chain_table.c.event_hash)
                    .order_by(self.audit_chain_table.c.sequence.desc()).limit(1)
                ).first()
                connection.execute(insert(self.audit_chain_head_table).values(
                    id=1,
                    sequence=last_event.sequence if last_event else 0,
                    head_hash=last_event.event_hash if last_event else GENESIS_HASH,
                ))
        except IntegrityError:
            # Another application process initialized the singleton head first.
            pass
        self.engagements = DatabaseMapping(self.engine, self.engagement_table, Engagement, self.lock)
        self.approvals = DatabaseMapping(self.engine, self.approval_table, Approval, self.lock)
        self.findings = DatabaseMapping(self.engine, self.finding_table, Finding, self.lock)
        self.audit = AuditCollection(
            self.engine, self.audit_table, self.audit_chain_table,
            self.audit_chain_head_table, self.lock,
        )

    def decide_approval(
        self, approval_id: UUID, approved: bool, reviewer: str,
        expires_at: datetime | None,
    ) -> Approval:
        """Record exactly one reviewer decision using a database compare-and-swap."""
        with self.lock, self.engine.begin() as connection:
            row = connection.execute(
                select(self.approval_table.c.payload).where(
                    self.approval_table.c.id == str(approval_id)
                )
            ).scalar_one_or_none()
            if row is None:
                raise KeyError(approval_id)
            item = Approval.model_validate_json(row)
            if item.approved_by is not None or item.consumed:
                raise PermissionError("approval decision is immutable")
            if approved and item.requested_by == reviewer:
                raise PermissionError("requester cannot approve their own request")
            updated = item.model_copy(update={
                "approved": approved, "approved_by": reviewer, "expires_at": expires_at,
            })
            result = connection.execute(
                update(self.approval_table)
                .where(self.approval_table.c.id == str(approval_id))
                .where(self.approval_table.c.payload == row)
                .values(payload=updated.model_dump_json())
            )
            if result.rowcount != 1:
                raise PermissionError("approval was concurrently decided")
            return updated

    def consume_approval(
        self, approval_id: UUID, envelope_sha256: str, actor: str,
    ) -> Approval:
        """Atomically consume a one-time grant for its original requester only."""
        with self.lock, self.engine.begin() as connection:
            row = connection.execute(
                select(self.approval_table.c.payload).where(
                    self.approval_table.c.id == str(approval_id)
                )
            ).scalar_one_or_none()
            if row is None:
                raise KeyError(approval_id)
            item = Approval.model_validate_json(row)
            if not item.approved or item.consumed:
                raise PermissionError("approval is not available for consumption")
            if item.requested_by != actor:
                raise PermissionError("only the original requester may consume this approval")
            if item.envelope_sha256 != envelope_sha256:
                raise PermissionError("approval does not match the requested action envelope")
            if item.requested_by == item.approved_by:
                raise PermissionError("requester and reviewer must be different actors")
            if item.expires_at is None or item.expires_at <= datetime.now(UTC):
                raise PermissionError("approval has expired or has no expiry")
            updated = item.model_copy(update={"consumed": True})
            result = connection.execute(
                update(self.approval_table)
                .where(self.approval_table.c.id == str(approval_id))
                .where(self.approval_table.c.payload == row)
                .values(payload=updated.model_dump_json())
            )
            if result.rowcount != 1:
                raise PermissionError("approval was concurrently consumed")
            return updated

    def log(self, event: AuditEvent) -> AuditEvent:
        self.audit.append(event)
        return event

    def verify_audit_chain(self) -> dict:
        return self.audit.verify()

    def create_audit_checkpoint(self) -> dict:
        secret = os.getenv("SOCKBOI_AUDIT_CHECKPOINT_KEY", "")
        if len(secret) < 32:
            raise RuntimeError("SOCKBOI_AUDIT_CHECKPOINT_KEY must contain at least 32 characters")
        verification = self.audit.verify()
        if not verification["valid"]:
            raise RuntimeError("audit chain integrity verification failed")
        checkpoint = {
            "algorithm": "HMAC-SHA256",
            "event_count": verification["event_count"],
            "head_hash": verification["head_hash"],
        }
        message = f'{checkpoint["event_count"]}:{checkpoint["head_hash"]}'.encode("utf-8")
        checkpoint["signature"] = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
        return checkpoint


store = DatabaseStore()
