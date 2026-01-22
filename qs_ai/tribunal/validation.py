# qs_ai/tribunal/validation.py
from qs_ai.tribunal.exceptions import ScottScheduleValidationError


def validate_bound_quantity(bound_quantity):
    if bound_quantity.approval_snapshot_id is None:
        raise ScottScheduleValidationError(
            "Bound quantity is not approved"
        )

    if bound_quantity.confidence_at_binding < 0.6:
        raise ScottScheduleValidationError(
            "Quantity confidence below tribunal threshold"
        )

    if not bound_quantity.evidence_ids:
        raise ScottScheduleValidationError(
            "Quantity has no supporting evidence"
        )
