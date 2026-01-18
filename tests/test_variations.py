import pytest
from qs_ai.commercial.variation_approval import VariationApprovalEngine

def test_invalid_vo_transition():
    engine = VariationApprovalEngine()

    class DummyVO:
        status = "QS_VALUED"
        vo_id = "VO1"
        __dict__ = {"status": "QS_VALUED", "vo_id": "VO1"}

    with pytest.raises(RuntimeError):
        engine.transition(DummyVO(), "CERTIFIED", approved_by="Client")
