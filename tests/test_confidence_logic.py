from geometry_rules import count_openings

def test_missing_quantity_reduces_confidence(default_context):
    entries = [
        {"Room": "Living"},  # Quantity missing
        {"Room": "Bedroom"},
    ]

    res = count_openings(entries, default_context, "doors")

    assert res["quantity"] == 2
    assert res["confidence"] < 1.0
