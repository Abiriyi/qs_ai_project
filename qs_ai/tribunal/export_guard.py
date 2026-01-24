from qs_ai.approval.models import JointApprovalStatus
from qs_ai.tribunal.exceptions import TribunalExportError

def enforce_joint_signature(statement):
    if statement.status != JointApprovalStatus.FULLY_SIGNED:
        raise RuntimeError(
            "Joint expert statement cannot be exported "
            "until both experts have countersigned."
        )

def enforce_export_readiness(context):
    """
    Hard gate before tribunal export.
    Context must expose verification flags.
    """

    if not getattr(context, "approvals_verified", False):
        raise TribunalExportError("Unapproved artefacts exist")

    if not getattr(context, "joint_signatures_verified", False):
        raise TribunalExportError("Joint expert signatures incomplete")

    if not getattr(context, "evidence_verified", False):
        raise TribunalExportError("Evidence sufficiency check failed")

    return True