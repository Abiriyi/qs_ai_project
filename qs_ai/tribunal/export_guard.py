from qs_ai.approval.models import JointApprovalStatus


def enforce_joint_signature(statement):
    if statement.status != JointApprovalStatus.FULLY_SIGNED:
        raise RuntimeError(
            "Joint expert statement cannot be exported "
            "until both experts have countersigned."
        )
