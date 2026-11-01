"""Shared test configuration for authenticated API tests."""
import json
import os

from sockboi.security import key_record

os.environ["SOCKBOI_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SOCKBOI_AUDIT_CHECKPOINT_KEY"] = "test-checkpoint-secret-" + "x" * 32
os.environ["SOCKBOI_API_KEYS"] = json.dumps([
    key_record("test-key", "test-operator", "test-tenant", ["admin", "operator", "reviewer"]),
    key_record("tenant-b-key", "tenant-b-reader", "tenant-b", ["reader"]),
    key_record("reviewer-key", "independent-reviewer", "test-tenant", ["reviewer"]),
    key_record("peer-operator-key", "peer-operator", "test-tenant", ["operator"]),
])
