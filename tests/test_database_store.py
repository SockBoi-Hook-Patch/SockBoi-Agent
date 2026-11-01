from sockboi.models import AuditEvent, Engagement, ScopeAsset
from sockboi.store import DatabaseStore


def test_database_store_persists_records_across_instances(tmp_path):
    database_url = "sqlite+pysqlite:///" + str(tmp_path / "sockboi-test.db")
    first = DatabaseStore(database_url)
    engagement = Engagement(
        name="Persistence lab",
        authorization_ref="ROE-PERSIST",
        owner="operator",
        scope=[ScopeAsset(kind="domain", value="persist.example.test")],
        tenant_id="tenant-persist",
    )
    first.engagements[engagement.id] = engagement
    first.log(AuditEvent(
        engagement_id=engagement.id, event_type="test.persisted", actor="test"
    ))

    second = DatabaseStore(database_url)
    loaded = second.engagements[engagement.id]
    assert loaded.tenant_id == "tenant-persist"
    assert loaded.name == "Persistence lab"
    assert [event.event_type for event in second.audit] == ["test.persisted"]


def test_database_store_clear(tmp_path):
    database_url = "sqlite+pysqlite:///" + str(tmp_path / "sockboi-clear.db")
    database = DatabaseStore(database_url)
    engagement = Engagement(
        name="Clear lab",
        authorization_ref="ROE-CLEAR",
        owner="operator",
        scope=[ScopeAsset(kind="domain", value="clear.example.test")],
    )
    database.engagements[engagement.id] = engagement
    assert len(database.engagements) == 1
    database.engagements.clear()
    assert len(database.engagements) == 0


def test_audit_hash_chain_verifies_and_detects_tampering(tmp_path):
    database_url = "sqlite+pysqlite:///" + str(tmp_path / "sockboi-chain.db")
    database = DatabaseStore(database_url)
    engagement = Engagement(
        name="Audit chain lab", authorization_ref="ROE-CHAIN",
        owner="operator",
        scope=[ScopeAsset(kind="domain", value="chain.example.test")],
        tenant_id="tenant-chain",
    )
    database.engagements[engagement.id] = engagement
    database.log(AuditEvent(
        engagement_id=engagement.id, event_type="engagement.created",
        actor="operator", detail={"authorization_ref": "ROE-CHAIN"},
    ))
    database.log(AuditEvent(
        engagement_id=engagement.id, event_type="approval.requested",
        actor="operator", detail={"target": "chain.example.test"},
    ))
    verified = database.verify_audit_chain()
    assert verified["valid"] is True
    assert verified["event_count"] == 2
    assert len(verified["head_hash"]) == 64
    with database.engine.begin() as connection:
        from sqlalchemy import update
        connection.execute(
            update(database.audit_chain_table)
            .where(database.audit_chain_table.c.sequence == 1)
            .values(payload='{"tampered":true}')
        )
    assert database.verify_audit_chain()["valid"] is False


def test_audit_chain_uses_genesis_for_empty_stream(tmp_path):
    database = DatabaseStore("sqlite+pysqlite:///" + str(tmp_path / "empty-chain.db"))
    result = database.verify_audit_chain()
    assert result["valid"] is True
    assert result["event_count"] == 0
    assert result["head_hash"] == "0" * 64


def test_audit_chain_serializes_concurrent_writers_across_store_instances(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from uuid import uuid4

    database_url = "sqlite+pysqlite:///" + str(tmp_path / "concurrent-chain.db")
    first = DatabaseStore(database_url)
    second = DatabaseStore(database_url)

    def append(index):
        target = first if index % 2 else second
        target.log(AuditEvent(
            engagement_id=uuid4(), event_type="concurrency.test",
            actor=f"worker-{index}", detail={"index": index},
        ))

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(append, range(32)))
    result = first.verify_audit_chain()
    assert result["valid"] is True
    assert result["event_count"] == 32
    assert result["head_matches"] is True


def test_audit_checkpoint_is_signed_and_requires_external_secret(tmp_path, monkeypatch):
    database = DatabaseStore("sqlite+pysqlite:///" + str(tmp_path / "checkpoint.db"))
    monkeypatch.delenv("SOCKBOI_AUDIT_CHECKPOINT_KEY", raising=False)
    try:
        database.create_audit_checkpoint()
    except RuntimeError as exc:
        assert "at least 32 characters" in str(exc)
    else:
        raise AssertionError("checkpoint must fail closed without a strong secret")
    monkeypatch.setenv("SOCKBOI_AUDIT_CHECKPOINT_KEY", "test-checkpoint-secret-" + "x" * 32)
    checkpoint = database.create_audit_checkpoint()
    assert checkpoint["algorithm"] == "HMAC-SHA256"
    assert len(checkpoint["signature"]) == 64


def test_audit_head_initializes_from_existing_chain_on_upgrade(tmp_path):
    database_url = "sqlite+pysqlite:///" + str(tmp_path / "upgrade-chain.db")
    first = DatabaseStore(database_url)
    first.log(AuditEvent(
        engagement_id=__import__("uuid").uuid4(),
        event_type="before.head.migration", actor="operator",
    ))
    first.audit_chain_head_table.drop(first.engine)

    upgraded = DatabaseStore(database_url)
    assert upgraded.verify_audit_chain()["valid"] is True
    upgraded.log(AuditEvent(
        engagement_id=__import__("uuid").uuid4(),
        event_type="after.head.migration", actor="operator",
    ))
    result = upgraded.verify_audit_chain()
    assert result["valid"] is True
    assert result["event_count"] == 2
