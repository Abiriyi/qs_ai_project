from qs_ai.evidence.capture import capture_evidence

def approve_override(override_record, approver_id):
    evidence = capture_evidence(
        category="approval",
        source="approval_engine",
        description="QS override approved",
        payload={
            "item_id": override_record.item_id,
            "approved_quantity": override_record.new_quantity,
        },
        created_by=approver_id,
    )

    override_record.status = "APPROVED"
    override_record.evidence.append(evidence)
    return override_record
