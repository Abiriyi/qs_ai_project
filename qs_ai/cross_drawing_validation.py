from collections import defaultdict
from statistics import mean

def validate_quantity_consistency(entries):
    """
    Compare quantities across drawing sources.
    Returns: (ok: bool, penalty: float, message: str)
    """
    by_source = defaultdict(list)

    for e in entries:
        src = e.get("source", "plan")
        qty = e.get("Quantity") or e.get("Qty") or 1
        by_source[src].append(int(qty))

    if len(by_source) <= 1:
        return True, 0.0, "Single drawing source"

    totals = {src: sum(qs) for src, qs in by_source.items()}

    if len(set(totals.values())) == 1:
        return True, 0.0, "Quantities consistent across drawings"

    penalty = 0.15
    msg = f"Inconsistent quantities across drawings: {totals}"

    return False, penalty, msg

def validate_geometry_consistency(entries, field):
    values = [e.get(field) for e in entries if e.get(field) is not None]

    if len(values) < 2:
        return True, 0.0, "Insufficient data for consistency check"

    ref = values[0]
    for v in values[1:]:
        if abs(v - ref) > 0.15:
            return False, 0.3, f"Inconsistent {field} values"

    return True, 0.0, f"{field} values consistent"

