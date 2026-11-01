"""Shared test configuration for authenticated API tests."""
import json
import os

from sockboi.security import key_record

os.environ["SOCKBOI_API_KEYS"] = json.dumps([
    key_record("test-key", "test-operator", "test-tenant", ["admin", "operator", "reviewer"]),
    key_record("tenant-b-key", "tenant-b-reader", "tenant-b", ["reader"]),
])
