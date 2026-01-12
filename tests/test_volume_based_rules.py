from geometry_rules import reinforced_concrete_rule

def test_rc_volume(default_context):
    entries = [
        {"length": 4.0, "width": 3.0, "thickness": 0.2},
    ]

    res = reinforced_concrete_rule(entries, default_context)

    assert round(res["quantity"], 3) == 2.4
    assert res["unit"] == "m3"
