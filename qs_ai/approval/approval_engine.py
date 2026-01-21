from uuid import uuid4
from datetime import datetime
from qs_ai.approval.models import ExpertApproval, ApprovalStatus
from qs_ai.approval.exceptions import ApprovalError


class ApprovalEngine:

    def submit(self, artefact_type, artefact_id):
        return ExpertApproval(
            approval_id=str(uuid4()),
            artefact_type=artefact_type,
            artefact_id=artefact_id,
            approved_by="",
            approved_role="",
            approval_datetime=datetime.utcnow(),
            status=ApprovalStatus.SUBMITTED
        )

    def approve(self, record, approver_name, role, signature):
        if record.status != ApprovalStatus.SUBMITTED:
            raise ApprovalError("Only submitted items can be approved")

        return ExpertApproval(
            approval_id=record.approval_id,
            artefact_type=record.artefact_type,
            artefact_id=record.artefact_id,
            approved_by=approver_name,
            approved_role=role,
            approval_datetime=datetime.utcnow(),
            status=ApprovalStatus.APPROVED,
            digital_signature=signature
        )

    def reject(self, record, remarks):
        return ExpertApproval(
            **{**record.__dict__, "status": ApprovalStatus.REJECTED, "remarks": remarks}
        )
