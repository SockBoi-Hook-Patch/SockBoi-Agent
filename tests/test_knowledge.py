from sockboi.knowledge import SkillLibrary


def test_skill_documents_are_isolated_by_tenant():
    library = SkillLibrary()
    content = "# Internal Runbook\nprivate tenant-only marker"
    tenant_a = library.ingest_markdown("runbook.md", content, tenant_id="tenant-a")
    tenant_b = library.ingest_markdown("runbook.md", content, tenant_id="tenant-b")

    assert tenant_a.document_id != tenant_b.document_id
    assert tenant_a.content_sha256 == tenant_b.content_sha256
    assert [item["document_id"] for item in library.search(
        "private tenant-only marker", tenant_id="tenant-a",
    )] == [tenant_a.document_id]
    assert [item["document_id"] for item in library.search(
        "private tenant-only marker", tenant_id="tenant-b",
    )] == [tenant_b.document_id]
    assert library.search("private tenant-only marker", tenant_id="tenant-c") == []
