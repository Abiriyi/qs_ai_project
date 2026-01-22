# qs_ai/tribunal/scott_builder.py
from uuid import uuid4
from datetime import datetime
from qs_ai.tribunal.scott_models import (
    ScottSchedule,
    ScottItem,
    ScottQuantityReference,
)
from qs_ai.tribunal.validation import validate_bound_quantity


class ScottScheduleBuilder:

    def build(
        self,
        contract_reference: str,
        prepared_by: str,
        issues,
        bound_quantities,
    ) -> ScottSchedule:

        items = []

        for issue in issues:
            bq = bound_quantities[issue.issue_id]

            validate_bound_quantity(bq)

            claimed_amount = round(
                bq.final_quantity * bq.rate, 2
            )

            items.append(
                ScottItem(
                    item_id=str(uuid4()),
                    issue=issue,
                    quantity_ref=ScottQuantityReference(
                        bound_quantity_id=bq.bound_id
                    ),
                    rate=bq.rate,
                    claimed_amount=claimed_amount,
                    confidence=bq.confidence_at_binding,
                    approval_snapshot_id=bq.approval_snapshot_id,
                )
            )

        return ScottSchedule(
            schedule_id=str(uuid4()),
            title="Scott Schedule of Issues",
            contract_reference=contract_reference,
            prepared_by=prepared_by,
            prepared_at=datetime.utcnow(),
            items=items,
        )
