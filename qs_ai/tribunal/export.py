from qs_ai.tribunal.models import TribunalPack


def generate_tribunal_pack(claim, approvals, evidence_bundle):
    """
    Assemble a tribunal-ready export pack.
    This is a façade used by E2E tests.
    """
    return TribunalPack(
        claim_id=claim.claim_id,
        approvals=approvals,
        evidence=evidence_bundle,
        status="READY_FOR_TRIBUNAL",
    )
