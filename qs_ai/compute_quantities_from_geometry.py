# compute_quantities_from_geometry.py

from qs_ai.geometry_rules import RULE_REGISTRY
from qs_ai.cross_drawing_validation import (
    validate_quantity_consistency,
    validate_geometry_consistency
)

# Local defaults (do NOT rely on boq_generator globals)
DEFAULTS = {
    "room_height": 3.0,
    "slab_depth": 0.15,
}

def compute_quantities_from_geometry(agg, context, defaults=None):
    if defaults is None:
        defaults = DEFAULTS

    computed = {}

    for canonical_key, payload in agg.items():
        key = canonical_key.lower()
        handler = RULE_REGISTRY.get(key)

        # ---------------- Fallback if no handler ----------------
        if handler is None:
            units = payload.get("units", {})
            qty = sum(units.values()) if units else 0.0

            computed[key] = {
                "quantity": round(qty, 4),
                "unit": next(iter(units.keys()), None),
                "justification": "Fallback to parsed numeric quantities",
                "confidence": 0.4
            }
            continue

        # ---------------- Rule execution ----------------
        res = handler(payload["entries"], context)

        confidence = res.get("confidence", 1.0)
        notes = []

        ok, penalty, msg = validate_quantity_consistency(payload["entries"])
        if not ok:
            confidence -= penalty
            notes.append(msg)

        ok, penalty, msg = validate_geometry_consistency(
            payload["entries"], "storey_height"
        )
        if not ok:
            confidence -= penalty
            notes.append(msg)

        confidence = max(round(confidence, 2), 0.0)

        computed[key] = {
            "quantity": round(float(res.get("quantity", 0.0)), 4),
            "unit": res.get("unit"),
            "justification": res.get("justification", "") + (
                " | Cross-check: " + " ; ".join(notes) if notes else ""
            ),
            "confidence": confidence
        }

    return computed

