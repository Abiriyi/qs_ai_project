from qs_ai.qs_override.models import QSOverrideRecord
from qs_ai.qs_override.exceptions import (
    InvalidOverrideError,
    PermissionDeniedError,
)
from qs_ai.evidence.capture import capture_evidence

ALLOWED_ROLES = {"QS", "Senior QS", "Associate", "Partner"}


class QSOverrideService:
    def __init__(self, storage_backend):
        self.storage = storage_backend

    def submit_override(self, item_id, old_qty, new_qty, reason, qs_id):
        evidence = capture_evidence(
            category="override",
            source="qs_override_service",
            description="QS quantity override submitted",
            payload={
                "item_id": item_id,
                "old_quantity": old_qty,
                "new_quantity": new_qty,
                "reason": reason,
            },
            created_by=qs_id,
        )

        record = QSOverrideRecord(
            item_id=item_id,
            old_quantity=old_qty,
            new_quantity=new_qty,
            reason=reason,
            submitted_by=qs_id,
            status="PENDING_APPROVAL",
            evidence=[evidence],
        )

        self.storage.save_override(record)
        return record

