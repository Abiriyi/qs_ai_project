from uuid import uuid4
from datetime import date
from qs_ai.audit.change_log import log_event
from qs_ai.commercial.variation_models import VariationOrder

class VariationEngine:

    def create_variation(
        self,
        instruction_ref: str,
        description: str,
        valued_by: str,
        items: list,
    ) -> VariationOrder:

        vo = VariationOrder(
            vo_id=str(uuid4()),
            instruction_ref=instruction_ref,
            description=description,
            issued_date=date.today(),
            valued_by=valued_by,
            items=items,
            status="QS_VALUED",
        )

        log_event(
            event_type="VARIATION_VALUED",
            entity_id=vo.vo_id,
            details={
                "instruction_ref": instruction_ref,
                "valued_by": valued_by,
                "item_count": len(items),
            },
        )

        return vo
