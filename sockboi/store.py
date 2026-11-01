"""Development-only in-memory store. Replace with transactional persistence before production."""
from uuid import UUID

from .models import Approval, AuditEvent, Engagement, Finding


class MemoryStore:
    def __init__(self) -> None:
        self.engagements: dict[UUID, Engagement] = {}
        self.approvals: dict[UUID, Approval] = {}
        self.findings: dict[UUID, Finding] = {}
        self.audit: list[AuditEvent] = []

    def log(self, event: AuditEvent) -> AuditEvent:
        self.audit.append(event)
        return event


store = MemoryStore()
