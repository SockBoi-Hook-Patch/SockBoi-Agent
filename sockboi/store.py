"""SQLAlchemy-backed persistence for engagement, approval, finding and audit records."""
from __future__ import annotations

import os
from collections.abc import Iterator, MutableMapping
from threading import RLock
from typing import TypeVar
from uuid import UUID

from sqlalchemy import (\n    Column,\n    Integer,\n    MetaData,\n    String,\n    Table,\n    Text,\n    create_engine,\n    delete,\n    insert,\n    select,\n)
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from .models import Approval, AuditEvent, Engagement, Finding

ModelT = TypeVar("ModelT")


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
        self.engine = engine
        self.table = table
        self.model = model
        self.lock = lock

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
    def __init__(self, engine: Engine, table: Table, lock: RLock):
        self.engine = engine
        self.table = table
        self.lock = lock

    def append(self, event: AuditEvent) -> None:
        with self.lock, self.engine.begin() as connection:
            connection.execute(insert(self.table).values(
                event_id=str(event.id), engagement_id=str(event.engagement_id),
                payload=event.model_dump_json(),
            ))

    def __iter__(self) -> Iterator[AuditEvent]:
        with self.engine.connect() as connection:
            payloads = connection.execute(
                select(self.table.c.payload).order_by(self.table.c.sequence)
            ).scalars().all()
        return iter(AuditEvent.model_validate_json(payload) for payload in payloads)

    def clear(self) -> None:
        with self.lock, self.engine.begin() as connection:
            connection.execute(delete(self.table))


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
            Column("engagement_id", String(36), nullable=False),
            Column("payload", Text, nullable=False),
        )
        metadata.create_all(self.engine)
        self.engagements = DatabaseMapping(self.engine, self.engagement_table, Engagement, self.lock)
        self.approvals = DatabaseMapping(self.engine, self.approval_table, Approval, self.lock)
        self.findings = DatabaseMapping(self.engine, self.finding_table, Finding, self.lock)
        self.audit = AuditCollection(self.engine, self.audit_table, self.lock)

    def log(self, event: AuditEvent) -> AuditEvent:
        self.audit.append(event)
        return event


store = DatabaseStore()
