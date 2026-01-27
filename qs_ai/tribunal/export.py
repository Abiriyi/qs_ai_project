from qs_ai.tribunal.models import TribunalPack


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
        status="READY_FOR_TRIBUNAL",
    )

