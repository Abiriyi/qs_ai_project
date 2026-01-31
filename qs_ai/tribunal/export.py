from qs_ai.tribunal.models import TribunalPack
from qs_ai.version import get_release_identity

def generate_tribunal_pack(
    project_id: str,
    claims=None,
    approvals=None,
    evidence=None,
):
    if approvals is None:
        raise ValueError("Tribunal pack requires approved data")

    return TribunalPack(
        project_id=project_id,
        claims=claims or [],
        approvals=approvals,
        evidence=evidence or [],
        system_release=get_release_identity(),
        status="READY_FOR_TRIBUNAL",
    )

