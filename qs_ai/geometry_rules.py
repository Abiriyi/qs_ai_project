"""
QS-grade geometry rules engine for BoQ quantity computation.

Each rule:
- Accepts (entries, context)
- Validates measurement context
- Computes defensible quantities
- Emits audit evidence
"""

from typing import List
from qs_ai.measurement_context import MeasurementContext
from qs_ai.evidence.capture import capture_evidence


# -------------------------------------------------
# Rule requirements (must match actual logic)
# -------------------------------------------------
RULE_REQUIREMENTS = {
    "plastering": ["length", "height"],
    "painting": ["length", "height"],
    "tiling": ["area"],
    "ceiling finish": ["area"],
    "skirting": ["perimeter"],
    "doors": ["Quantity"],
    "windows": ["Quantity"],
    "reinforced concrete": ["length", "width", "thickness"],
}


# -------------------------------------------------
# Utilities
# -------------------------------------------------
def _safe_float(v, fallback=0.0) -> float:
    try:
        if v is None:
            return fallback
        return float(str(v).replace(",", "").strip())
    except Exception:
        return fallback


def validate_geometry(entries, context, requires):
    missing = set()

    for r in requires:
        if hasattr(context, r):
            if getattr(context, r) in (None, 0):
                missing.add(r)
        else:
            if not any(e.get(r) for e in entries):
                missing.add(r)

    if missing:
        return False, f"Missing geometry/context: {', '.join(sorted(missing))}"

    return True, ""


def rule_guard(rule_name: str, entries, context):
    if not context.confirmed:
        return False, {
            "quantity": 0.0,
            "unit": None,
            "justification": "Measurement context not confirmed",
            "confidence": 0.0,
        }

    requires = RULE_REQUIREMENTS.get(rule_name, [])
    ok, reason = validate_geometry(entries, context, requires)

    if not ok:
        return False, {
            "quantity": 0.0,
            "unit": None,
            "justification": reason,
            "confidence": 0.0,
        }

    return True, None


# -------------------------------------------------
# WALL-BASED (m2)
# -------------------------------------------------
def plastering_rule(entries, context):
    ok, failure = rule_guard("plastering", entries, context)
    if not ok:
        return failure

    area = sum(_safe_float(e["length"]) * _safe_float(e["height"]) for e in entries)

    evidence = capture_evidence(
        category="geometry",
        source="plastering_rule",
        description="Wall plastering area",
        payload={
            "entries": entries,
            "formula": "Σ(length × height)",
            "result": area,
        },
    )

    return {
        "quantity": round(area, 2),
        "unit": "m2",
        "justification": "Computed from wall geometry",
        "confidence": 1.0,
        "evidence": [evidence],
    }


def painting_rule(entries, context):
    ok, failure = rule_guard("painting", entries, context)
    if not ok:
        return failure

    area = sum(_safe_float(e["length"]) * _safe_float(e.get("height") or context.storey_height) for e in entries)

    evidence = capture_evidence(
        category="geometry",
        source="painting_rule",
        description="Wall painting area",
        payload={
            "entries": entries,
            "formula": "Σ(length × height)",
            "result": area,
        },
    )

    return {
        "quantity": round(area, 2),
        "unit": "m2",
        "justification": "Σ wall lengths × storey height",
        "confidence": context.storey_height_confidence,
        "evidence": [evidence],
    }


# -------------------------------------------------
# FLOOR / CEILING (m2)
# -------------------------------------------------
def floor_area_rule(entries, context):
    ok, failure = rule_guard("tiling", entries, context)
    if not ok:
        return failure

    total = 0.0
    breakdown = []

    for e in entries:
        area = _safe_float(e.get("area"))
        if area <= 0:
            area = _safe_float(e.get("length")) * _safe_float(e.get("width"))

        if area > 0:
            total += area
            breakdown.append(f"{e.get('Room', '?')}: {area:.2f}")

    evidence = capture_evidence(
        category="geometry",
        source="floor_area_rule",
        description="Floor / ceiling area",
        payload={
            "entries": entries,
            "breakdown": breakdown,
            "total": total,
        },
    )

    return {
        "quantity": round(total, 2),
        "unit": "m2",
        "justification": "; ".join(breakdown),
        "confidence": context.scale_confidence,
        "evidence": [evidence],
    }


# -------------------------------------------------
# SKIRTING (m)
# -------------------------------------------------
def skirting_rule(entries, context):
    ok, failure = rule_guard("skirting", entries, context)
    if not ok:
        return failure

    total = 0.0
    breakdown = []

    for e in entries:
        perimeter = _safe_float(e.get("perimeter") or e.get("length"))
        openings = _safe_float(e.get("openings_width"))
        net = max(0.0, perimeter - openings)

        total += net
        breakdown.append(f"{e.get('Room','?')}: {net:.2f}")

    evidence = capture_evidence(
        category="geometry",
        source="skirting_rule",
        description="Skirting length",
        payload={
            "entries": entries,
            "breakdown": breakdown,
            "total": total,
        },
    )

    return {
        "quantity": round(total, 2),
        "unit": "m",
        "justification": "; ".join(breakdown),
        "confidence": context.scale_confidence,
        "evidence": [evidence],
    }


# -------------------------------------------------
# OPENINGS (No.)
# -------------------------------------------------
def count_openings(entries, context, item_key):
    total = 0
    assumed = 0
    breakdown = []

    for e in entries:
        room = e.get("Room", "?")
        qty = e.get("Quantity") or e.get("Qty")

        if qty is None:
            q = 1
            assumed += 1
            breakdown.append(f"{room}: 1 (assumed)")
        else:
            q = int(qty)
            breakdown.append(f"{room}: {q}")

        total += q

    confidence = max(1.0 - (0.2 * assumed), 0.3)

    evidence = capture_evidence(
        category="count",
        source=f"{item_key}_count",
        description=f"{item_key.capitalize()} count",
        payload={
            "entries": entries,
            "breakdown": breakdown,
            "assumed": assumed,
            "total": total,
        },
    )

    return {
        "quantity": total,
        "unit": "No.",
        "justification": "; ".join(breakdown),
        "confidence": round(confidence, 2),
        "evidence": [evidence],
    }


# -------------------------------------------------
# CONCRETE (m3)
# -------------------------------------------------
def reinforced_concrete_rule(entries, context):
    ok, failure = rule_guard("reinforced concrete", entries, context)
    if not ok:
        return failure

    total = 0.0
    breakdown = []

    for e in entries:
        l = _safe_float(e.get("length"))
        w = _safe_float(e.get("width"))
        t = _safe_float(e.get("thickness") or context.slab_thickness)

        vol = l * w * t
        if vol > 0:
            total += vol
            breakdown.append(f"{l}×{w}×{t} = {vol:.3f}")

    evidence = capture_evidence(
        category="geometry",
        source="reinforced_concrete_rule",
        description="Reinforced concrete volume",
        payload={
            "entries": entries,
            "breakdown": breakdown,
            "total": total,
        },
    )

    return {
        "quantity": round(total, 3),
        "unit": "m3",
        "justification": "; ".join(breakdown),
        "confidence": context.scale_confidence,
        "evidence": [evidence],
    }


# -------------------------------------------------
# RULE REGISTRY
# -------------------------------------------------
RULE_REGISTRY = {
    "plastering": plastering_rule,
    "painting": painting_rule,
    "blockwork": plastering_rule,
    "partition walls": plastering_rule,
    "tiling": floor_area_rule,
    "ceiling finish": floor_area_rule,
    "skirting": skirting_rule,
    "doors": lambda e, c: count_openings(e, c, "doors"),
    "windows": lambda e, c: count_openings(e, c, "windows"),
    "reinforced concrete": reinforced_concrete_rule,
    "concrete": reinforced_concrete_rule,
}

