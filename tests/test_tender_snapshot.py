import pytest
from qs_ai.commercial.tender_service import TenderSnapshotService

def test_snapshot_blocks_pending_overrides():
    service = TenderSnapshotService()

    with pytest.raises(RuntimeError):
        service.issue_snapshot(
            boq_id="BOQ-001",
            revision=1,
            issued_by="A. SeniorQS",
            purpose="IFT",
            currency="USD",
            role="Senior QS",
        )
