from uuid import uuid4
from datetime import date
from qs_ai.audit.change_log import log_event

def remeasure_item(
    original_item_id: str,
    corrected_quantity: float,
    justification: str,
    measured_by: str,
):
    remeasurement_id = str(uuid4())

    log_event(
        event_type="REMEASUREMENT_DECLARED",
        entity_id=remeasurement_id,
        details={
            "original_item_id": original_item_id,
            "corrected_quantity": corrected_quantity,
            "justification": justification,
            "measured_by": measured_by,
            "date": date.today().isoformat(),
        },
    )

    return remeasurement_id
