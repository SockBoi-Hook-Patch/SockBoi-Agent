"""Untrusted Markdown knowledge ingestion and lexical retrieval.

Skill text is stored as reference material only. This module never executes content.
"""
import re
from dataclasses import dataclass
from hashlib import sha256

MAX_DOCUMENT_BYTES = 256_000


@dataclass(frozen=True)
class SkillDocument:
    document_id: str
    source: str
    title: str
    content: str
    content_sha256: str
    trusted_for_execution: bool = False


class SkillLibrary:
    def __init__(self) -> None:
        self._documents: dict[str, SkillDocument] = {}

    def ingest_markdown(self, source: str, content: str) -> SkillDocument:
        if not source.strip() or len(source) > 500:
            raise ValueError("source must be a non-empty identifier up to 500 characters")
        if not content.strip():
            raise ValueError("document content cannot be empty")
        raw = content.encode("utf-8")
        if len(raw) > MAX_DOCUMENT_BYTES:
            raise ValueError("document exceeds the 256 KB ingestion limit")
        digest = sha256(raw).hexdigest()
        document_id = digest[:16]
        title_match = re.search(r"(?m)^#\s+(.+)$", content)
        title = title_match.group(1).strip() if title_match else source.rsplit("/", 1)[-1]
        document = SkillDocument(
            document_id=document_id, source=source, title=title,
            content=content, content_sha256=digest,
        )
        self._documents[document_id] = document
        return document

    def search(self, query: str, limit: int = 5) -> list[dict[str, str]]:
        if not query.strip():
            return []
        terms = set(re.findall(r"[a-zA-Z0-9_ก-๙]+", query.lower()))
        scored: list[tuple[int, SkillDocument]] = []
        for document in self._documents.values():
            text = f"{document.title}\n{document.content}".lower()
            score = sum(text.count(term) for term in terms)
            if score:
                scored.append((score, document))
        scored.sort(key=lambda item: (-item[0], item[1].document_id))
        return [
            {"document_id": doc.document_id, "source": doc.source,
             "title": doc.title, "content_sha256": doc.content_sha256,
             "excerpt": doc.content[:1200], "trust": "untrusted_reference"}
            for _, doc in scored[:max(1, min(limit, 20))]
        ]


skill_library = SkillLibrary()
