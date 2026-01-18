from datetime import datetime
from uuid import uuid4
from qs_ai.qs_override.override_service import has_pending_overrides
from qs_ai.audit.change_log import log_event
from qs_ai.commercial.tender_snapshot import TenderSnapshot

class TenderSnapshotService:

    def issue_snapshot(
        self,
        boq_id: str,
        revision: int,
        issued_by: str,
        purpose: str,
        currency: str,
        role: str,
        notes: str = None,
    ) -> TenderSnapshot:

        if role not in {"Senior QS", "Commercial Manager"}:
            raise PermissionError("Insufficient authority to issue tender")

        if has_pending_overrides(boq_id):
            raise RuntimeError(
                "Cannot issue tender: unapproved QS overrides exist"
            )

        snapshot = TenderSnapshot(
            snapshot_id=str(uuid4()),
            boq_id=boq_id,
            revision=revision,
            issued_by=issued_by,
            issued_at=datetime.utcnow(),
            purpose=purpose,
            currency=currency,
            notes=notes,
        )

        log_event(
            event_type="TENDER_ISSUED",
            entity_id=snapshot.snapshot_id,
            details={
                "boq_id": boq_id,
                "revision": revision,
                "issued_by": issued_by,
                "purpose": purpose,
            },
        )

        return snapshot
