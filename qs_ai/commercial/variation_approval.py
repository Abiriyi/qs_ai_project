from qs_ai.audit.change_log import log_event

class VariationApprovalEngine:

    VALID_TRANSITIONS = {
        "QS_VALUED": ["APPROVED"],
        "APPROVED": ["CERTIFIED"],
    }

    def transition(self, vo, new_status, approved_by):
        if new_status not in self.VALID_TRANSITIONS.get(vo.status, []):
            raise RuntimeError(
                f"Invalid VO transition {vo.status} → {new_status}"
            )

        log_event(
            event_type="VARIATION_STATUS_CHANGED",
            entity_id=vo.vo_id,
            details={
                "from": vo.status,
                "to": new_status,
                "approved_by": approved_by,
            },
        )

        return vo.__class__(**{**vo.__dict__, "status": new_status})
