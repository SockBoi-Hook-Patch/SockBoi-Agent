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
