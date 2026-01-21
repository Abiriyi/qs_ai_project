from qs_ai.qs_override.exceptions import ApprovalRequiredError

def require_approval(record, stage: str):
    if not record.approved:
        raise ApprovalRequiredError(
            f"{stage} blocked: record {record.record_id} is not approved"
        )
