from geometry_rules import plastering_rule

def test_plastering_area(default_context):
    entries = [
        {"length": 5.0, "height": 3.0},
        {"length": 4.0, "height": 3.0},
    ]

    res = plastering_rule(entries, default_context)

    expected_area = (5 + 4) * 3

    assert round(res["quantity"], 2) == expected_area
    assert res["unit"] == "m2"
