# geometry_rules.py
"""
Context-aware geometry rules engine for BoQ quantity computation.

Each handler:
- Accepts (entries, context)
- Validates measurement context
- Computes defensible quantities
- Returns:
    {
        "quantity": float,
        "unit": str,
        "justification": str
    }

This file is QS-grade and audit-safe.
"""

from typing import List, Dict, Any
from qs_ai.measurement_context import MeasurementContext


# -------------------------------
# Utilities
# -------------------------------
RULE_REQUIREMENTS = {
    "plastering": ["perimeter", "storey_height"],
    "painting": ["perimeter", "storey_height"],
    "tiling": ["area"],
    "ceiling finish": ["area"],
    "skirting": ["perimeter"],
    "doors": ["Quantity"],
    "windows": ["Quantity"],
    "reinforced concrete": ["area", "slab_thickness"],
}

def _safe_float(v, fallback=0.0) -> float:
    try:
        if v is None:
            return float(fallback)
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().replace(",", "")
        return float(s) if s else float(fallback)
    except Exception:
        return float(fallback)


def _context_guard(context: MeasurementContext, requires: List[str]):
    """
    Ensure required context fields exist and are confirmed.
    """
    if not context.confirmed:
        return False, "Measurement context not confirmed"

    for r in requires:
        if getattr(context, r, None) in (None, 0):
            return False, f"Required context missing: {r}"

    return True, ""

def compute_quantity_confidence(entries, context, requires):
    """
    Confidence scoring based on geometry + context completeness.
    """
    score = 1.0
    missing = 0
    total = len(requires)

    for r in requires:
        if hasattr(context, r):
            if getattr(context, r) in (None, 0):
                missing += 1
        else:
            if not any(e.get(r) for e in entries):
                missing += 1

    if total > 0:
        score -= missing / total

    if not context.confirmed:
        score -= 0.2

    return max(round(score, 2), 0.0)


# -------------------------------
# WALL-BASED MEASUREMENTS (m2)
# -------------------------------

def plastering_rule(entries, context):
    if not context.confirmed:
        return {
            "quantity": 0.0,
            "unit": "m2",
            "justification": "Measurement context not confirmed",
            "confidence": 0.0,
        }

    total_length = 0.0
    height = context.storey_height

    for e in entries:
        length = e.get("length")
        h = e.get("height") or height
        if length and h:
            total_length += float(length)

    if total_length == 0 or not height:
        return {
            "quantity": 0.0,
            "unit": "m2",
            "justification": "Insufficient wall geometry",
            "confidence": 0.4,
        }

    area = total_length * height

    return {
        "quantity": round(area, 2),
        "unit": "m2",
        "justification": "Σ wall lengths × storey height",
        "confidence": min(
            context.scale_confidence,
            context.storey_height_confidence,
        ),
    }

   
def painting_rule(entries, context):
    if not context.confirmed:
        return {
            "quantity": 0.0,
            "unit": "m2",
            "justification": "Measurement context not confirmed",
            "confidence": 0.0,
        }

    total_length = 0.0
    height = context.storey_height

    for e in entries:
        length = e.get("length")
        h = e.get("height") or height
        if length and h:
            total_length += float(length)

    if total_length == 0 or not height:
        return {
            "quantity": 0.0,
            "unit": "m2",
            "justification": "Insufficient wall geometry",
            "confidence": 0.4,
        }

    area = total_length * height

    return {
        "quantity": round(area, 2),
        "unit": "m2",
        "justification": "Σ wall lengths × storey height",
        "confidence": min(
            context.scale_confidence,
            context.storey_height_confidence,
        ),
    }


# -------------------------------
# FLOOR / CEILING (m2)
# -------------------------------

def floor_area(entries, context):
    ok, reason = validate_geometry(
        entries,
        context,
        RULE_REQUIREMENTS["tiling"]
    )

    if not ok:
        return {
            "quantity": 0.0,
            "unit": "m2",
            "justification": reason,
            "confidence": 0.0
        }

    total = 0.0
    parts = []

    for e in entries:
        area = _safe_float(e.get("area"))
        if area <= 0:
            area = _safe_float(e.get("length")) * _safe_float(e.get("width"))

        if area > 0:
            total += area
            parts.append(f"{e.get('Room','?')}: {area:.2f}")

    confidence = compute_quantity_confidence(
        entries,
        context,
        RULE_REQUIREMENTS["tiling"]
    )
    
    return {
        "quantity": round(total, 2),
        "unit": "m2",
        "justification": "; ".join(parts),
        "confidence": confidence
    }


# -------------------------------
# SKIRTING (m)
# -------------------------------

def skirting(entries, context):
    ok, reason = validate_geometry(
        entries,
        context,
        RULE_REQUIREMENTS["skirting"]
    )

    if not ok:
        return {
            "quantity": 0.0,
            "unit": "m2",
            "justification": reason,
            "confidence": 0.0
        }

    total = 0.0
    parts = []

    for e in entries:
        perimeter = _safe_float(e.get("perimeter") or e.get("length"))
        openings = _safe_float(e.get("openings_width"))

        net = max(0.0, perimeter - openings)
        total += net
        parts.append(f"{e.get('Room','?')}: {net:.2f}")

    confidence = compute_quantity_confidence(
        entries,
        context,
        RULE_REQUIREMENTS["skirting"]
    )
    
    return {
        "quantity": round(total, 4),
        "unit": "m",
        "justification": "; ".join(parts),
        "confidence": confidence
    }

# -------------------------------
# OPENINGS (No.)
# -------------------------------
def compute_openings_confidence(entries, context):
    """
    Confidence for doors/windows counting
    """
    if not context.confirmed:
        return 0.0

    explicit = 0
    inferred = 0

    for e in entries:
        if e.get("Quantity") is not None or e.get("Qty") is not None:
            explicit += 1
        else:
            inferred += 1

    total = explicit + inferred
    if total == 0:
        return 0.0

    ratio = explicit / total

    # Weighted confidence
    confidence = 0.6 + (0.4 * ratio)

    return round(min(confidence, 1.0), 2)

def count_openings(entries, context, item_key):
    total = 0
    assumed = 0
    parts = []

    for e in entries:
        room = e.get("Room", "?")
        qty = e.get("Quantity") or e.get("Qty")

        if qty is None:
            q = 1
            assumed += 1
            parts.append(f"{room}: 1 (assumed)")
        else:
            q = int(qty)
            parts.append(f"{room}: {q}")

        total += q

    confidence = 1.0
    if assumed:
        confidence -= 0.2 * assumed

    return {
        "quantity": total,
        "unit": "No.",
        "justification": "; ".join(parts),
        "confidence": max(round(confidence, 2), 0.3),
    }

# -------------------------------
# CONCRETE (m3)
# -------------------------------

def reinforced_concrete_rule(entries, context):
    total = 0.0

    for e in entries:
        l = e.get("length")
        w = e.get("width")
        t = e.get("thickness") or context.slab_thickness

        if l and w and t:
            total += float(l) * float(w) * float(t)

    if total == 0:
        return {
            "quantity": 0.0,
            "unit": "m3",
            "justification": "Missing RC geometry",
            "confidence": 0.3,
        }

    return {
        "quantity": round(total, 3),
        "unit": "m3",
        "justification": "Length × width × thickness",
        "confidence": context.scale_confidence,
    }

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
        return False, f"Missing geometry: {', '.join(sorted(missing))}"

    return True, ""
def rule_guard(rule_name: str, entries, context):
    """
    Standard guard applied to ALL geometry rules.
    """
    if not context.confirmed:
        return False, {
            "quantity": 0.0,
            "unit": None,
            "justification": "Measurement context not confirmed"
        }

    requires = RULE_REQUIREMENTS.get(rule_name, [])
    ok, reason = validate_geometry(entries, context, requires)

    if not ok:
        return False, {
            "quantity": 0.0,
            "unit": None,
            "justification": reason
        }

    return True, None
# -------------------------------
# RULE REGISTRY
# -------------------------------

RULE_REGISTRY = {
    # Wall-based
    "plastering": plastering_rule,
    "painting": plastering_rule,
    "blockwork": plastering_rule,
    "partition walls": plastering_rule,

    # Floor-based
    "tiling": floor_area,
    "ceiling finish": floor_area,
    "ground floor slab": floor_area,

    # Linear
    "skirting": skirting,

    # Count
    "doors": lambda entries, context: count_openings(entries, context, "doors"),
    "windows": lambda entries, context: count_openings(entries, context, "windows"),

    # Volume
    "reinforced concrete": reinforced_concrete_rule,
    "concrete": reinforced_concrete_rule,
}

# --- Public rule aliases (test + API stability) ---

floor_area_rule = floor_area
skirting_rule = skirting
count_openings_rule = count_openings
