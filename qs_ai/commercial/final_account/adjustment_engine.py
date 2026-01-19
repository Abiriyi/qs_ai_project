from datetime import datetime
from .models import Adjustment
from uuid import uuid4

class AdjustmentEngine:

    @staticmethod
    def create_adjustment(
        boq_item_code: str,
        adjustment_type: str,
        quantity_delta: float,
        rate: float,
        approved_by: str,
        reference: str,
    ) -> Adjustment:

        value = round(quantity_delta * rate, 2)

        return Adjustment(
            adjustment_id=str(uuid4()),
            boq_item_code=boq_item_code,
            adjustment_type=adjustment_type,
            quantity_delta=quantity_delta,
            rate=rate,
            value=value,
            approved_by=approved_by,
            approval_date=datetime.utcnow(),
            reference=reference,
        )
