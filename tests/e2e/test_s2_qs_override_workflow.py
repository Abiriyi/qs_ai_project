import pytest
from qs_ai.qs_override.override_service import QSOverrideService
from qs_ai.qs_override.exceptions import InvalidOverrideError
from qs_ai.approval.approval_engine import ApprovalEngine

def test_override_requires_approval_before_application():
    service = QSOverrideService(storage_backend={})
    approval_engine = ApprovalEngine()

    override = service.submit_override(
        item_id="PLASTER_001",
        old_qty=100,
        new_qty=120,
        reason="Design change on site",
        qs_id="qs_001",
    )

    assert override["status"] == "PENDING_APPROVAL"


def test_override_without_reason_fails():
    service = QSOverrideService(storage_backend={})

    with pytest.raises(InvalidOverrideError):
        service.submit_override(
            item_id="ITEM1",
            old_qty=10,
            new_qty=12,
            reason="",
            qs_id="qs_001",
        )

