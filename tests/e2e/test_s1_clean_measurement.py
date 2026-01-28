import pytest
from qs_ai.geometry_rules import plastering_rule

def test_clean_measurement_generates_defensible_quantity(
    simple_geometry,
    confirmed_context
):
    result = plastering_rule(simple_geometry, confirmed_context)

    assert result["quantity"] > 0
    assert result["unit"] == "m2"
    assert "justification" in result
    assert "evidence" in result
    assert len(result["evidence"]) == 1
