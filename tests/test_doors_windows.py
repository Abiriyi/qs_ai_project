from geometry_rules import count_openings

def test_doors_basic_count(default_context):
    entries = [
        {"Room": "Living", "Quantity": 2},
        {"Room": "Bedroom", "Quantity": 1},
        {"Room": "Kitchen", "Quantity": 1},
    ]

    res = count_openings(entries, default_context, "doors")

    assert res["quantity"] == 4
    assert res["unit"] == "No."
    assert "Living" in res["justification"]
