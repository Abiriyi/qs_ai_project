"""
BoQ Composition Engine

Resolves final BoQ quantities by applying
only APPROVED QS overrides to computed quantities.
"""

from typing import Dict, List

from qs_ai.qs_override.models import QSOverrideRecord
from qs_ai.qs_override.approval_engine import ApprovalState
from qs_ai.audit.change_log import AuditLog
from qs_ai.qs_override.approval_guard import require_approval

class BoQComposer:
    """
    Composes final BoQ quantities for tender / valuation use.
    """

    def __init__(self, audit_log: AuditLog):
        self.audit_log = audit_log

    def compose(self, quantity_records):
        approved = []

        for r in quantity_records:
            require_approval(r, stage="BoQ composition")
            approved.append(r)

        return approved

    # --------------------------------------------------
    # Internal handlers
    # --------------------------------------------------

    def _apply_override(self, *, item_code, computed, override):
        """
        Replace computed quantity with approved override.
        """

        self.audit_log.append(
            actor=override.actor,
            action="APPLY_APPROVED_OVERRIDE",
            item_code=item_code,
            previous_value=computed["quantity"],
            new_value=override.override_quantity,
            justification=override.justification,
            confidence_before=computed.get("confidence"),
            confidence_after=override.override_confidence,
            metadata={
                "override_id": override.override_id,
                "approval_state": override.state,
            },
        )

        return {
            "quantity": override.override_quantity,
            "unit": computed["unit"],
            "confidence": override.override_confidence,
            "justification": (
                f"{computed.get('justification', '')} | "
                f"QS Override Applied: {override.justification}"
            ),
            "source": "QS_OVERRIDE",
        }

    def _accept_computed(self, item_code, computed):
        """
        Accept computed quantity unchanged.
        """

        self.audit_log.append(
            actor="SYSTEM",
            action="ACCEPT_COMPUTED_QUANTITY",
            item_code=item_code,
            previous_value=None,
            new_value=computed["quantity"],
            justification="No approved QS override",
            confidence_before=None,
            confidence_after=computed.get("confidence"),
        )

        return {
            **computed,
            "source": "AUTO_COMPUTED",
        }
