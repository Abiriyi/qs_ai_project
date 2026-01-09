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
from measurement_context import MeasurementContext


# -------------------------------
# Utilities
# -------------------------------

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


# -------------------------------
# WALL-BASED MEASUREMENTS (m2)
# -------------------------------

# geometry_rules.py

def plastering(entries, context):
    if not context.confirmed:
        return {
            "quantity": 0,
            "unit": "m2",
            "justification": "Measurement context not confirmed"
        }

    if not context.storey_height:
        return {
            "quantity": 0,
            "unit": "m2",
            "justification": "Storey height missing"
        }

    # 🔒 geometry availability guard
    if not any(e.get("perimeter") or e.get("length") for e in entries):
        return {
            "quantity": 0,
            "unit": "m2",
            "justification": "Geometry not available from drawings"
        }

    total = 0.0
    for e in entries:
        perimeter = e.get("perimeter") or e.get("length") or 0.0
        total += float(perimeter) * context.storey_height

    return {
        "quantity": round(total, 2),
        "unit": "m2",
        "justification": "Perimeter × confirmed storey height"
    }

# geometry_rules.py

def painting(entries, context):
    if not context.confirmed:
        return {
            "quantity": 0,
            "unit": "m2",
            "justification": "Measurement context not confirmed"
        }

    if not context.storey_height:
        return {
            "quantity": 0,
            "unit": "m2",
            "justification": "Storey height missing"
        }

    # 🔒 geometry availability guard
    if not any(e.get("perimeter") or e.get("length") for e in entries):
        return {
            "quantity": 0,
            "unit": "m2",
            "justification": "Geometry not available from drawings"
        }

    total = 0.0
    for e in entries:
        perimeter = e.get("perimeter") or e.get("length") or 0.0
        total += float(perimeter) * context.storey_height

    return {
        "quantity": round(total, 2),
        "unit": "m2",
        "justification": "Perimeter × confirmed storey height"
    }

# -------------------------------
# FLOOR / CEILING (m2)
# -------------------------------

def floor_area(entries, context):
    """
    Floor / ceiling / slab areas (m2).

    Accepts:
    - explicit area from parser
    - OR length × width
    - Context-aware guards
    """

    if not context.confirmed:
        return {
            "quantity": 0.0,
            "unit": "m2",
            "justification": "Measurement context not confirmed"
        }

    # Geometry availability guard
    if not any(
        e.get("area") or (e.get("length") and e.get("width"))
        for e in entries
    ):
        return {
            "quantity": 0.0,
            "unit": "m2",
            "justification": "Floor geometry not available from drawings"
        }

    total = 0.0
    parts = []

    for e in entries:
        area = _safe_float(e.get("area"))

        if area <= 0:
            length = _safe_float(e.get("length"))
            width = _safe_float(e.get("width"))
            area = length * width

        if area > 0:
            total += area
            parts.append(f"{e.get('Room','?')}: {area:.2f} m2")

    return {
        "quantity": round(total, 2),
        "unit": "m2",
        "justification": "; ".join(parts)
    }

# -------------------------------
# SKIRTING (m)
# -------------------------------

def skirting(entries: List[Dict[str, Any]], context: MeasurementContext):
    """
    Skirting length = wall perimeter minus openings widths
    """
    ok, reason = _context_guard(context, [])
    if not ok:
        return {"quantity": 0.0, "unit": "m", "justification": reason}

    total = 0.0
    parts = []

    for e in entries:
        perimeter = _safe_float(e.get("perimeter") or e.get("length"))
        openings = _safe_float(e.get("openings_width") or 0)

        net = max(0.0, perimeter - openings)
        total += net
        parts.append(f"{e.get('Room','?')}: {net:.2f}")

    return {
        "quantity": round(total, 4),
        "unit": "m",
        "justification": "; ".join(parts)
    }


# -------------------------------
# OPENINGS (No.)
# -------------------------------

def count_openings(entries: List[Dict[str, Any]], context: MeasurementContext):
    """
    Doors / Windows count
    """
    ok, reason = _context_guard(context, [])
    if not ok:
        return {"quantity": 0, "unit": "No.", "justification": reason}

    total = 0
    parts = []

    for e in entries:
        qty = e.get("Quantity") or e.get("Qty")
        q = int(_safe_float(qty, fallback=1))
        total += q
        parts.append(f"{e.get('Room','?')}: {q}")

    return {
        "quantity": total,
        "unit": "No.",
        "justification": "; ".join(parts)
    }


# -------------------------------
# CONCRETE (m3)
# -------------------------------

def reinforced_concrete(entries: List[Dict[str, Any]], context: MeasurementContext):
    """
    Concrete volumes:
    - area × slab_thickness
    """
    REQUIRES = ["slab_thickness"]

    ok, reason = _context_guard(context, REQUIRES)
    if not ok:
        return {"quantity": 0.0, "unit": "m3", "justification": reason}

    total = 0.0
    parts = []

    for e in entries:
        area = _safe_float(e.get("area"))
        if area <= 0:
            continue

        vol = area * context.slab_thickness
        total += vol
        parts.append(
            f"{e.get('Room','?')}: {area:.2f} × {context.slab_thickness:.2f}"
        )

    return {
        "quantity": round(total, 4),
        "unit": "m3",
        "justification": "; ".join(parts)
    }


# -------------------------------
# RULE REGISTRY
# -------------------------------

RULE_REGISTRY = {
    # Wall-based
    "plastering": plastering,
    "painting": plastering,
    "blockwork": plastering,
    "partition walls": plastering,

    # Floor-based
    "tiling": floor_area,
    "ceiling finish": floor_area,
    "ground floor slab": floor_area,

    # Linear
    "skirting": skirting,

    # Count
    "doors": count_openings,
    "windows": count_openings,

    # Volume
    "reinforced concrete": reinforced_concrete,
    "concrete": reinforced_concrete,
}


