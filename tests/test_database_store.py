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
