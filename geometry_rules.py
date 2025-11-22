# geometry_rules.py
"""
Geometry rules engine for BoQ quantity computation.

Handlers accept a list of parsed entries (dictionaries) and a defaults dict and
return a dict: { "quantity": float, "unit": str, "justification": str }.
"""

from typing import List, Dict, Any
from math import isfinite

def _safe_float(v, fallback=0.0):
    try:
        if v is None:
            return float(fallback)
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip()
        if s == "":
            return float(fallback)
        # remove common thousand separators
        s = s.replace(",", "")
        return float(s)
    except Exception:
        return float(fallback)

def handler_walls(entries: List[Dict[str,Any]], defaults: Dict[str,Any]):
    """
    Compute wall/partition/plastering/painting areas.
    Expected fields on each entry:
      - length (m) or perimeter (m)
      - height (m) or room_height fallback
      - openings: optional list of dicts with 'area' field or numeric openings_area
    Returns m2.
    """
    total = 0.0
    parts = []
    default_height = _safe_float(defaults.get("room_height", 3.0))

    for e in entries:
        length = _safe_float(e.get("length") or e.get("perimeter") or 0.0)
        height = _safe_float(e.get("height") or e.get("room_height") or default_height)
        openings_area = 0.0

        # openings may be list of dicts with area or numeric field
        openings = e.get("openings") or e.get("Openings") or []
        if isinstance(openings, list):
            for o in openings:
                if isinstance(o, dict):
                    openings_area += _safe_float(o.get("area", 0.0))
                else:
                    openings_area += _safe_float(o)
        else:
            openings_area = _safe_float(e.get("openings_area") or e.get("openings") or 0.0)

        area = max(0.0, length * height - openings_area)
        total += area
        parts.append(f"{e.get('Room','?')}: {length:.3f}*{height:.3f}-{openings_area:.3f}={area:.3f}")

    return {"quantity": round(total, 4), "unit": "m2", "justification": "; ".join(parts)}


def handler_floor(entries: List[Dict[str,Any]], defaults: Dict[str,Any]):
    """
    Compute floor/tiling/ceiling area.
    Uses 'area' if present, else length*width fallback.
    """
    total = 0.0
    parts = []
    for e in entries:
        area = _safe_float(e.get("area"))
        if not area or area == 0.0:
            length = _safe_float(e.get("length"))
            width = _safe_float(e.get("width"))
            area = length * width
        total += area
        parts.append(f"{e.get('Room','?')}: {area:.3f}")
    return {"quantity": round(total, 4), "unit": "m2", "justification": "; ".join(parts)}


def handler_openings_count(entries: List[Dict[str,Any]], defaults: Dict[str,Any]):
    """
    Count openings (doors/windows). If parsed entries carry explicit quantity numeric fields,
    sum them; else count items.
    """
    total = 0
    parts = []
    for e in entries:
        qty = e.get("Quantity") or e.get("Qty") or e.get("quantity")
        if qty is not None:
            qn = int(_safe_float(qty, fallback=0))
        else:
            qn = 1
        total += qn
        parts.append(f"{e.get('Room','?')}:{qn}")
    return {"quantity": int(total), "unit": "No.", "justification": "; ".join(parts)}


def handler_skirting(entries: List[Dict[str,Any]], defaults: Dict[str,Any]):
    """
    Compute skirting length (m) — usually equals wall lengths minus openings.
    Uses 'length' or 'perimeter' per entry.
    """
    total = 0.0
    parts = []
    for e in entries:
        length = _safe_float(e.get("length") or e.get("perimeter") or 0.0)
        openings_width = _safe_float(e.get("openings_width") or e.get("openings_length") or 0.0)
        net = max(0.0, length - openings_width)
        total += net
        parts.append(f"{e.get('Room','?')}: {length:.3f}-{openings_width:.3f}={net:.3f}")
    return {"quantity": round(total, 4), "unit": "m", "justification": "; ".join(parts)}


def handler_reinforced_concrete(entries: List[Dict[str,Any]], defaults: Dict[str,Any]):
    """
    Compute concrete volumes (m3). Common inputs:
     - area * depth (for slabs) where 'area' and 'thickness'/'depth' present
     - column: cross_section_area * length
    Fallback: use parsed Quantity sum (if present).
    """
    total = 0.0
    parts = []
    default_depth = _safe_float(defaults.get("slab_depth", 0.15))  # 150mm default

    for e in entries:
        # prefer explicit volume
        vol = _safe_float(e.get("volume") or e.get("vol") or e.get("m3"))
        if vol and vol > 0:
            total += vol
            parts.append(f"{e.get('Room','?')}: vol={vol:.3f}")
            continue

        area = _safe_float(e.get("area"))
        depth = _safe_float(e.get("thickness") or e.get("depth") or default_depth)
        if area and area > 0 and depth > 0:
            v = area * depth
            total += v
            parts.append(f"{e.get('Room','?')}: {area:.3f}*{depth:.3f}={v:.3f}")
            continue

        # column style: cross_section_area * length
        cs_area = _safe_float(e.get("cross_section_area"))
        length = _safe_float(e.get("length"))
        if cs_area and length:
            v = cs_area * length
            total += v
            parts.append(f"{e.get('Room','?')}: {cs_area:.3f}*{length:.3f}={v:.3f}")
            continue

        # fallback to parsed qty
        qty = _safe_float(e.get("Quantity") or e.get("Qty") or 0.0)
        total += qty
        parts.append(f"{e.get('Room','?')}: fallback qty {qty:.3f}")

    return {"quantity": round(total, 4), "unit": "m3", "justification": "; ".join(parts)}


# Registry mapping canonical keys (lowercase) -> handler
RULE_REGISTRY = {
    "plastering": handler_walls,
    "painting": handler_walls,
    "blockwork": handler_walls,
    "partition walls": handler_walls,
    "tiling": handler_floor,
    "ground floor slab": handler_floor,
    "ceiling finish": handler_floor,
    "skirting": handler_skirting,
    "doors": handler_openings_count,
    "windows": handler_openings_count,
    "reinforced concrete": handler_reinforced_concrete,
    "concrete": handler_reinforced_concrete,
    # add more mappings as needed
}
