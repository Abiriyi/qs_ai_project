from cross_drawing_validation import validate_geometry_consistency

def test_storey_height_inconsistency():
    entries = [
        {"height": 3.0},
        {"height": 2.7},
    ]

    ok, penalty, msg = validate_geometry_consistency(
        entries, field="height"
    )

    assert ok is False
    assert penalty > 0
    assert "inconsistent" in msg.lower()
