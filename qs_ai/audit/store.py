from typing import Optional
from qs_ai.audit.models import AuditEvent


class AuditStore:
    """
    Append-only audit event store.
    """

    def __init__(self):
        self._events: list[AuditEvent] = []

    def last_hash(self) -> Optional[str]:
        if not self._events:
            return None
        return self._events[-1].event_hash

    def append(self, event: AuditEvent):
        self._events.append(event)

    def all_events(self):
        return list(self._events)
