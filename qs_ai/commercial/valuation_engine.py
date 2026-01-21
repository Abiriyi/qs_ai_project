from uuid import uuid4
from datetime import date
from qs_ai.audit.change_log import log_event
from qs_ai.commercial.valuation_models import Valuation, ValuationLine
from qs_ai.qs_override.approval_guard import require_approval
class ValuationEngine:

    def value(self, boq_items):
        for item in boq_items:
            require_approval(item, stage="Valuation")

    def create_valuation(
        self,
        snapshot_id: str,
        valuation_no: int,
        prepared_by: str,
        valuation_date: date,
        lines: list[ValuationLine],
        retention_percent: float,
    ) -> Valuation:

        for line in lines:
            if line.executed_quantity_to_date > line.tender_quantity:
                raise ValueError(
                    f"Over-valuation detected for item {line.boq_item_id}"
                )

        valuation = Valuation(
            valuation_id=str(uuid4()),
            snapshot_id=snapshot_id,
            valuation_no=valuation_no,
            valuation_date=valuation_date,
            prepared_by=prepared_by,
            lines=lines,
            retention_percent=retention_percent,
        )

        log_event(
            event_type="VALUATION_CREATED",
            entity_id=valuation.valuation_id,
            details={
                "snapshot_id": snapshot_id,
                "valuation_no": valuation_no,
                "prepared_by": prepared_by,
            },
        )

        return valuation
