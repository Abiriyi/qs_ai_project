from qs_ai.qs_override.models import QSOverrideRecord
from qs_ai.qs_override.exceptions import InvalidOverrideError
from qs_ai.evidence.capture import capture_evidence


class QSOverrideService:
    def __init__(self, storage_backend):
        self.storage = storage_backend

    def submit_override(self, item_id, old_qty, new_qty, reason, qs_id):
        if not reason or not reason.strip():
            raise InvalidOverrideError("QS override requires a written reason")

        evidence = capture_evidence(
            category="override",
            source="qs_override_service",
            description="QS quantity override submitted",
            payload={
                "boq_item_code": item_id,
                "old_quantity": old_qty,
                "new_quantity": new_qty,
                "reason": reason,
            },
            created_by=qs_id,
        )

        record = QSOverrideRecord(
            boq_item_code=item_id,
            base_quantity=old_qty,
            overridden_quantity=new_qty,
            reason=reason,
            created_by=qs_id,
            approval_state="SUBMITTED",
        )

        if hasattr(self.storage, "save_override"):
            self.storage.save_override(record)

        return record


