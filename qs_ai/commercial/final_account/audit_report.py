from datetime import datetime


class FinalAccountAuditReport:

    def generate(self, final_account) -> dict:
        report = {
            "final_account_id": final_account.final_account_id,
            "contract_id": final_account.contract_id,
            "generated_at": datetime.utcnow().isoformat(),
            "lines": [],
        }

        for line in final_account.lines:
            report["lines"].append({
                "boq_item_code": line.boq_item_code,
                "description": line.description,
                "original_quantity": line.original_quantity,
                "final_quantity": line.final_quantity,
                "original_value": line.original_value,
                "final_value": line.final_value,
                "adjustments": [
                    {
                        "adjustment_id": a.adjustment_id,
                        "type": a.adjustment_type,
                        "quantity_delta": a.quantity_delta,
                        "rate": a.rate,
                        "value": a.value,
                        "approved_by": a.approved_by,
                        "approval_date": a.approval_date.isoformat(),
                        "reference": a.reference,
                    }
                    for a in line.adjustments
                ],
            })

        return report
