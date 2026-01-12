import pytest
from qs_ai.boq_generator import populate_besmm4_from_parsed


def test_qs_gate_blocks_low_confidence(default_context):
    parsed = [
        {"Element": "Door", "Room": "Living"}  # no quantity → low confidence
    ]

    with pytest.raises(RuntimeError):
        populate_besmm4_from_parsed(parsed, default_context)
