from .exceptions import (
    MissingApprovalError,
    MissingReferenceError,
    AuditFailureError,
)


class FinalAccountAuditEngine:
    """
    Tribunal-grade audit validation.
    """

    def audit(self, final_account):
        issues = []

        for line in final_account.lines:
            for adj in line.adjustments:

                if not adj.approved_by:
                    issues.append(
                        f"{line.boq_item_code}: Adjustment {adj.adjustment_id} missing approver"
                    )

                if not adj.reference:
                    issues.append(
                        f"{line.boq_item_code}: Adjustment {adj.adjustment_id} missing instruction reference"
                    )

        if issues:
            raise AuditFailureError(issues)

        return True
