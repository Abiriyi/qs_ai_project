from datetime import datetime
from qs_ai.approval.models import (
    JointApprovalStatus,
    JointExpertSignature,
)
from qs_ai.approval.exceptions import ApprovalError


class JointCountersignatureEngine:

    def sign(self, statement, expert, digital_signature):
        if statement.status == JointApprovalStatus.FULLY_SIGNED:
            raise ApprovalError("Statement already fully signed")

        if any(s.expert_id == expert["id"] for s in statement.signatures):
            raise ApprovalError("Expert has already signed")

        signature = JointExpertSignature(
            expert_id=expert["id"],
            name=expert["name"],
            role=expert["role"],
            organisation=expert["organisation"],
            signed_at=datetime.utcnow(),
            digital_signature=digital_signature,
        )

        statement.signatures.append(signature)

        if len(statement.signatures) == 1:
            statement.status = JointApprovalStatus.SIGNED_BY_EXPERT_A
        elif len(statement.signatures) == 2:
            statement.status = JointApprovalStatus.FULLY_SIGNED

        return statement
