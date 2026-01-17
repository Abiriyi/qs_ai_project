import pytest
from qs_ai.qs_override.override_service import QSOverrideService
from qs_ai.qs_override.storage import InMemoryOverrideStore
from qs_ai.qs_override.exceptions import InvalidOverrideError, PermissionDeniedError


def test_valid_override_submission():
    store = InMemoryOverrideStore()
    service = QSOverrideService(store)

    record = service.submit_override(
        boq_item_code="BESMM4-12.01",
        description="Internal plaster to blockwork",
        base_quantity=120.0,
        overridden_quantity=135.0,
        unit="m2",
        reason="Additional returns at columns not shown on GA",
        created_by="A. QS",
        created_role="Senior QS",
    )

    assert record.delta() == 15.0
    assert record.approval_state == "DRAFT"


def test_override_requires_change():
    service = QSOverrideService(InMemoryOverrideStore())

    with pytest.raises(InvalidOverrideError):
        service.submit_override(
            boq_item_code="X",
            description="Test",
            base_quantity=10,
            overridden_quantity=10,
            unit="m",
            reason="No change",
            created_by="QS",
            created_role="QS",
        )


def test_role_enforcement():
    service = QSOverrideService(InMemoryOverrideStore())

    with pytest.raises(PermissionDeniedError):
        service.submit_override(
            boq_item_code="X",
            description="Test",
            base_quantity=10,
            overridden_quantity=12,
            unit="m",
            reason="Valid reason provided",
            created_by="Intern",
            created_role="Intern",
        )
