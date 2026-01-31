from uuid import uuid4
from datetime import datetime
from qs_ai.audit.models import AuditEvent
from qs_ai.audit.store import AuditStore


class AuditLogger:
    def __init__(self, store: AuditStore):
        self.store = store

    def log(
        self,
        *,
        event_type: str,
        actor_id: str,
        artefact_type: str,
        artefact_id: str,
        evidence_refs: list[str],
        details: dict,
    ) -> AuditEvent:

        previous_hash = self.store.last_hash()

        base_payload = {
            "event_type": event_type,
            "actor_id": actor_id,
            "artefact_type": artefact_type,
            "artefact_id": artefact_id,
            "timestamp": datetime.utcnow().isoformat(),
            "evidence_refs": evidence_refs,
            "details": details,
            "previous_hash": previous_hash,
        }

        payload_str = str(sorted(base_payload.items()))
        event_hash = AuditEvent.compute_hash(payload_str)

        event = AuditEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            actor_id=actor_id,
            artefact_type=artefact_type,
            artefact_id=artefact_id,
            timestamp=datetime.utcnow(),
            evidence_refs=evidence_refs,
            details=details,
            previous_hash=previous_hash,
            event_hash=event_hash,
        )

        self.store.append(event)
        return event
