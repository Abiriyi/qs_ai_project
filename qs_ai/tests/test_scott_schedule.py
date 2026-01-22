# qs_ai/tests/test_scott_schedule.py
import pytest
from qs_ai.tribunal.scott_builder import ScottScheduleBuilder
from qs_ai.tribunal.exceptions import ScottScheduleValidationError


def test_unapproved_quantity_blocks_scott_schedule(mock_issue, mock_unapproved_bq):
    builder = ScottScheduleBuilder()

    with pytest.raises(ScottScheduleValidationError):
        builder.build(
            contract_reference="Contract-001",
            prepared_by="QS Test",
            issues=[mock_issue],
            bound_quantities={mock_issue.issue_id: mock_unapproved_bq},
        )
