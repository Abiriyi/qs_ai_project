# boq_generator.py
"""
BESMM4 hierarchical BoQ generator with geometry-based quantity computation
and template-preserving Excel population.

Usage:
    from boq_generator import generate_besmm4_boq
    generate_besmm4_boq(parsed_entries_list, "output.xlsx", location="Kaduna")

Requires:
    - pandas
    - openpyxl
    - ai_pricing.get_rate_from_library(element, description, unit, location)
    - geometry_rules.py (in same directory)
"""

import os
from collections import defaultdict, OrderedDict
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import NamedStyle
from openpyxl.utils import get_column_letter
from ai_pricing import get_rate_from_library

from geometry_rules import RULE_REGISTRY

# ---------- Config ----------
DEFAULT_RATE = 0.0
TEMPLATE_PATH = "/mnt/data/besmm4_full_boq.xlsx"  # authoritative template (local path)
DEFAULTS = {
    "room_height": 3.0,
    "slab_depth": 0.15,
}

# Official high-level BESMM4 sections (1.0..8.0)
BESMM4_SECTIONS = OrderedDict([
    ("1.0", "Preliminaries"),
    ("2.0", "Substructure"),
    ("3.0", "Superstructure"),
    ("4.0", "Finishes"),
    ("5.0", "Fittings & Fixtures"),
    ("6.0", "Mechanical & Electrical Works"),
    ("7.0", "External Works"),
    ("8.0", "Provisional & Prime Cost Sums"),
])

# (same hierarchy and ELEMENT_KEYWORDS as before)
BESMM4_HIERARCHY = {
    "2.0": [
        ("2.1", "Excavating & Filling", [
            ("2.1.1", "Bulk excavation", "m3", "Excavation"),
            ("2.1.2", "Foundation excavation", "m3", "Excavation"),
            ("2.1.3", "Disposal off-site of excavated material", "m3", "Excavation"),
            ("2.1.4", "Filling obtained from excavated material", "m3", "Earthworks"),
        ]),
        ("2.2", "Concrete Work", [
            ("2.2.1", "Blinding concrete", "m3", "Concrete"),
            ("2.2.2", "Reinforced concrete in foundations", "m3", "Reinforced Concrete"),
            ("2.2.3", "Reinforced concrete ground floor slab", "m2", "Ground Floor Slab"),
        ]),
        ("2.3", "Damp Proofing & Membranes", [
            ("2.3.1", "Damp proof membrane", "m2", "Damp Proof Membrane"),
        ]),
    ],
    "3.0": [
        ("3.1", "Masonry / Blockwork", [
            ("3.1.1", "Blockwork 225mm thick in cement mortar", "m2", "Blockwork"),
            ("3.1.2", "Partition walls", "m2", "Partition Walls"),
        ]),
        ("3.2", "Structural Concrete & Steel", [
            ("3.2.1", "Reinforced concrete columns", "m3", "Reinforced Concrete"),
            ("3.2.2", "Structural steelwork", "t", "Steelwork"),
        ]),
        ("3.3", "Openings", [
            ("3.3.1", "Doors (supply & fix)", "No.", "Doors"),
            ("3.3.2", "Windows (supply & fix)", "No.", "Windows"),
        ]),
    ],
    "4.0": [
        ("4.1", "Internal Finishes", [
            ("4.1.1", "Internal plastering 12mm", "m2", "Plastering"),
            ("4.1.2", "Floor tiling (ceramic)", "m2", "Tiling"),
            ("4.1.3", "Skirting (supply & fix)", "m", "Skirting"),
            ("4.1.4", "Ceiling finishes (gypsum/POP/PVC)", "m2", "Ceiling Finish"),
            ("4.1.5", "Painting to walls (2 coats)", "m2", "Painting"),
        ]),
    ],
    "5.0": [
        ("5.1", "Fittings & Fixtures", [
            ("5.1.1", "Sanitary fittings (WC, basin, etc.)", "No.", "Sanitary Fittings"),
            ("5.1.2", "Kitchen fittings (complete)", "No.", "Kitchen Fittings"),
            ("5.1.3", "Wardrobes (supply & fix)", "No.", "Wardrobes"),
        ]),
    ],
    "6.0": [
        ("6.1", "Mechanical Services", [
            ("6.1.1", "Plumbing fittings (points)", "No.", "Plumbing"),
            ("6.1.2", "HVAC system (per system)", "No.", "HVAC"),
        ]),
        ("6.2", "Electrical Services", [
            ("6.2.1", "Lighting fittings", "No.", "Lighting"),
            ("6.2.2", "Power points", "No.", "Small Power"),
            ("6.2.3", "CCTV", "No.", "CCTV"),
        ]),
    ],
    "7.0": [
        ("7.1", "External Works", [
            ("7.1.1", "Paving", "m2", "Paving"),
            ("7.1.2", "Driveways", "m2", "Driveways"),
            ("7.1.3", "Landscaping", "m2", "Landscaping"),
        ]),
    ],
    "8.0": [
        ("8.1", "Provisional Sums", [
            ("8.1.1", "Specialized works (PC sum)", "item", "Specialized Works"),
            ("8.1.2", "Contingencies", "item", "Contingencies"),
        ]),
    ],
}

ELEMENT_KEYWORDS = {
    "excavation": "Excavation",
    "earthwork": "Earthworks",
    "foundation": "Foundations",
    "ground floor slab": "Ground Floor Slab",
    "slab": "Ground Floor Slab",
    "blockwork": "Blockwork",
    "partition": "Partition Walls",
    "plaster": "Plastering",
    "tiling": "Tiling",
    "painting": "Painting",
    "ceiling": "Ceiling Finish",
    "skirting": "Skirting",
    "door": "Doors",
    "window": "Windows",
    "sanitary": "Sanitary Fittings",
    "kitchen": "Kitchen Fittings",
    "plumbing": "Plumbing",
    "hvac": "HVAC",
    "lighting": "Lighting",
    "power": "Small Power",
    "cctv": "CCTV",
    "paving": "Paving",
    "driveway": "Driveways",
    "landscap": "Landscaping",
    "special": "Specialized Works",
    "conting": "Contingencies",
    "damp proof": "Damp Proof Membrane",
    "dpm": "Damp Proof Membrane",
    "reinforced concrete": "Reinforced Concrete",
    "concrete": "Concrete",
    "steel": "Steelwork",
    "skirting": "Skirting",
}

# ---------------- Helper Utilities ----------------

def _canonical_element_from_text(text: str):
    """Try to find a canonical element name from arbitrary text."""
    if text is None:
        return None
    t = text.lower()
    for k, canonical in ELEMENT_KEYWORDS.items():
        if k in t:
            return canonical
    return None

def _flatten_hierarchy():
    """Return mapping canonical_element -> (section_code, group_code, item_code, unit, description)"""
    flat = {}
    for sec_code, groups in BESMM4_HIERARCHY.items():
        sec_name = BESMM4_SECTIONS.get(sec_code, None) or ""
        for g_code, g_name, items in groups:
            for item_code, item_desc, unit, canonical in items:
                flat_key = (canonical or item_desc).lower()
                flat[flat_key] = {
                    "section_code": sec_code,
                    "section_name": BESMM4_SECTIONS.get(sec_code, sec_code),
                    "group_code": g_code,
                    "group_name": g_name,
                    "item_code": item_code,
                    "item_desc": item_desc,
                    "unit": unit,
                    "canonical": canonical or item_desc
                }
    return flat

FLAT_HIERARCHY = _flatten_hierarchy()

# ---------------- Aggregation & Mapping ----------------

def aggregate_parsed_entries(parsed_entries):
    """
    Aggregate parsed entries but preserve geometry and raw entries so rule handlers can compute quantities.
    Returns: dict keyed by canonical.lower() -> { 'units': defaultdict(float), 'descriptions': set(), 'entries': [raw entries...] }
    """
    agg = {}
    for e in parsed_entries:
        element = (e.get("Element") or "").strip()
        description = (e.get("Description") or "").strip()
        unit = (e.get("Unit") or "").strip() or "item"

        # preserve geometry/fields for rules
        preserved = {
            "Room": e.get("Room"),
            "Element": element,
            "Description": description,
            "Unit": unit,
            "Quantity": e.get("Quantity", e.get("Qty", None)),
            "length": e.get("length") or e.get("Length"),
            "width": e.get("width") or e.get("Width"),
            "height": e.get("height") or e.get("Height"),
            "area": e.get("area") or e.get("Area"),
            "thickness": e.get("thickness") or e.get("depth"),
            "openings": e.get("openings") or e.get("Openings") or e.get("openings_area"),
            # keep raw entry for fallback
            "raw": e
        }

        canonical = _canonical_element_from_text(element) or _canonical_element_from_text(description) or element or description
        if not canonical:
            continue
        key = canonical.lower()
        if key not in agg:
            agg[key] = {"units": defaultdict(float), "descriptions": set(), "entries": []}
        # keep numeric aggregation for fallback
        try:
            q = e.get("Quantity", e.get("Qty", 0)) or 0
            qn = float(str(q).replace(",", "")) if q is not None else 0.0
        except Exception:
            qn = 0.0
        agg[key]["units"][unit] += qn
        if description:
            agg[key]["descriptions"].add(description)
        agg[key]["entries"].append(preserved)
    return agg

# ---------------- Geometry-based computation ----------------

def compute_quantities_from_geometry(agg, defaults=None):
    """
    Given aggregated dict (from aggregate_parsed_entries), compute quantities per canonical key
    using handlers in geometry_rules.RULE_REGISTRY. Returns dict canonical.lower() -> {quantity, unit, justification}
    """
    if defaults is None:
        defaults = DEFAULTS
    computed = {}
    for canonical_key, payload in agg.items():
        handler = RULE_REGISTRY.get(canonical_key)
        if handler is None:
            # fallback: use aggregated numeric sum across units
            units = payload.get("units", {})
            qty = 0.0
            if units:
                # choose largest numeric sum (best-effort)
                try:
                    qty = max(units.values())
                except Exception:
                    qty = sum(units.values())
            computed[canonical_key] = {
                "quantity": round(float(qty), 4),
                "unit": next(iter(units.keys())) if units else None,
                "justification": "Fallback to parsed numeric quantities"
            }
        else:
            try:
                res = handler(payload.get("entries", []), defaults)
                # normalize
                q = float(res.get("quantity") or 0.0)
                computed[canonical_key] = {
                    "quantity": round(q, 4),
                    "unit": res.get("unit"),
                    "justification": res.get("justification", "")
                }
            except Exception as ex:
                # handler failed: fallback
                units = payload.get("units", {})
                qty = sum(units.values()) if units else 0.0
                computed[canonical_key] = {
                    "quantity": round(float(qty), 4),
                    "unit": next(iter(units.keys())) if units else None,
                    "justification": f"Handler error; fallback to parsed qty ({ex})"
                }
    return computed

# ---------------- Template population (load template & write into it) ----------------

def _build_full_item_list(include_empty=True):
    """
    Build a list of all items expected by the BESMM4_HIERARCHY.
    Returns list of dicts with item metadata.
    """
    items = []
    for sec_code, groups in BESMM4_HIERARCHY.items():
        sec_name = BESMM4_SECTIONS.get(sec_code, sec_code)
        for g_code, g_name, itms in groups:
            for item_code, item_desc, unit, canonical in itms:
                items.append({
                    "SectionCode": sec_code,
                    "SectionName": sec_name,
                    "GroupCode": g_code,
                    "GroupName": g_name,
                    "ItemCode": item_code,
                    "Description": item_desc,
                    "Unit": unit,
                    "Canonical": (canonical or item_desc),
                    "Quantity": 0.0,
                    "Rate": 0.0,
                    "Amount": 0.0,
                    "Justification": ""
                })
    return items

def populate_besmm4_from_parsed(parsed_entries, location="Kaduna", include_empty=True):
    """
    Map parsed entries into the full BESMM4 item list, compute quantities using geometry rules,
    and lookup rates. Returns: pandas.DataFrame of populated items.
    """
    agg = aggregate_parsed_entries(parsed_entries)
    computed = compute_quantities_from_geometry(agg, defaults=DEFAULTS)
    items = _build_full_item_list(include_empty=include_empty)

    # Map computed quantities into items
    for it in items:
        key = (it["Canonical"] or it["Description"]).lower()
        qty = 0.0
        justification = ""
        unit = it["Unit"]

        if key in computed:
            qty = computed[key].get("quantity", 0.0)
            # try to prefer template unit; if handler returned a different unit, keep item unit for display
            justification = computed[key].get("justification", "")
        else:
            # If not computed, try fuzzy match in agg (as before)
            # and fallback to parsed numeric totals
            found = False
            for agg_key, v in agg.items():
                if agg_key in key or key in agg_key:
                    qty = sum(v["units"].values())
                    found = True
                    break
            if not found:
                qty = 0.0
            justification = "No geometry handler; used parsed quantities" if qty > 0 else "No data"

        it["Quantity"] = float(round(qty, 4))
        it["Justification"] = justification

        # Rate lookup
        try:
            rate = get_rate_from_library(it["Canonical"], it["Description"], unit, location=location)
        except Exception:
            rate = None
        if rate is None:
            rate = DEFAULT_RATE
        it["Rate"] = float(rate)
        it["Amount"] = round(it["Quantity"] * it["Rate"], 2)

    df = pd.DataFrame(items)
    return df

def export_besmm4_using_template(populated_df: pd.DataFrame, output_path: str, template_path: str = None):
    """
    Load the template workbook (template_path), find Item Code rows and Quantity/Rate/Amount columns,
    write numeric values back into the template while preserving original formatting.
    Also create a hidden _audit sheet containing per-item justification.
    """
    if template_path is None:
        template_path = TEMPLATE_PATH

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found at {template_path}")

    wb = load_workbook(template_path)
    # assume BoQ is in the active sheet by default; if template has named sheet, tweak as needed
    ws = wb.active

    # find header row that contains 'Item Code' and 'Quantity'
    header_row = None
    item_code_col = None
    qty_col = None
    rate_col = None
    amount_col = None

    search_limit = min(60, ws.max_row)
    for r in range(1, search_limit + 1):
        values = [ (ws.cell(row=r, col=c).value if ws.cell(row=r, col=c).value is not None else "") for c in range(1, ws.max_column+1) ]
        joined = "|".join([str(v).strip().lower() for v in values if v is not None])
        if "item code" in joined or "itemcode" in joined:
            header_row = r
            # find exact columns by searching the row
            for c, val in enumerate(values, start=1):
                if not val:
                    continue
                v = str(val).strip().lower()
                if v in ("item code", "itemcode", "item_code"):
                    item_code_col = c
                if "quantity" in v and qty_col is None:
                    qty_col = c
                if "rate" in v and rate_col is None:
                    rate_col = c
                if "amount" in v and amount_col is None:
                    amount_col = c
            break

    if header_row is None or item_code_col is None or qty_col is None:
        # fallback strategy: assume template uses default layout similar to previous exporter:
        # Item Code col = 1, Description = 2, Unit = 3, Quantity = 4, Rate = 5, Amount = 6
        item_code_col = item_code_col or 1
        qty_col = qty_col or 4
        rate_col = rate_col or 5
        amount_col = amount_col or 6
        header_row = header_row or 1

    # Build an index mapping item_code -> row index in sheet for faster writes
    item_to_row = {}
    for r in range(header_row + 1, ws.max_row + 1):
        cell = ws.cell(row=r, column=item_code_col)
        if cell.value is None:
            continue
        code = str(cell.value).strip()
        if code == "":
            continue
        # store the first occurrence; if multiple, you'll need to refine logic
        if code not in item_to_row:
            item_to_row[code] = r

    # Write values into template
    # Preserve existing number formats when possible
    for _, row in populated_df.iterrows():
        item_code = str(row["ItemCode"]).strip()
        if item_code in item_to_row:
            r = item_to_row[item_code]
            # Quantity
            qcell = ws.cell(row=r, column=qty_col)
            qcell.value = float(row["Quantity"] or 0.0)
            # do not change style; but ensure numeric format exists
            try:
                # if cell had number_format, preserve; else set a generic number format
                if not qcell.number_format or qcell.number_format == 'General':
                    qcell.number_format = "#,##0.##"
            except Exception:
                pass

            # Rate
            rcell = ws.cell(row=r, column=rate_col)
            rcell.value = float(row["Rate"] or 0.0)
            try:
                if not rcell.number_format or rcell.number_format == 'General':
                    rcell.number_format = '"₦"#,##0.00'
            except Exception:
                pass

            # Amount
            acell = ws.cell(row=r, column=amount_col)
            acell.value = float(row["Amount"] or 0.0)
            try:
                if not acell.number_format or acell.number_format == 'General':
                    acell.number_format = '"₦"#,##0.00'
            except Exception:
                pass
        else:
            # Item code not found in template; skip or log (here we append below)
            continue

    # Create / populate audit sheet
    audit_name = "_audit"
    if audit_name in wb.sheetnames:
        audit = wb[audit_name]
        # clear existing rows (leave header) - simple approach: create new sheet instead
        wb.remove(audit)
    audit = wb.create_sheet(audit_name)
    audit.append(["ItemCode", "Description", "Unit", "Quantity", "Rate", "Amount", "Justification"])
    for _, row in populated_df.iterrows():
        audit.append([
            row["ItemCode"],
            row["Description"],
            row["Unit"],
            float(row["Quantity"] or 0.0),
            float(row["Rate"] or 0.0),
            float(row["Amount"] or 0.0),
            row.get("Justification", "")
        ])
    audit.sheet_state = "hidden"

    # Save workbook copy
    wb.save(output_path)
    return output_path

# ---------------- Public entrypoint ----------------

def generate_besmm4_boq(parsed_entries: list[dict], output_path: str, location: str = "Kaduna", template_path: str = None):
    """
    High-level function:
      - parsed_entries: list of dicts with keys Room, Element, Description, Unit, Quantity and optional geometry fields
      - output_path: path to .xlsx to write
      - location: passed to rate lookup
      - template_path: optional path to Excel template (defaults to TEMPLATE_PATH)
    """
    if not isinstance(parsed_entries, list):
        raise ValueError("parsed_entries must be a list of dicts")

    if template_path is None:
        template_path = TEMPLATE_PATH

    populated = populate_besmm4_from_parsed(parsed_entries, location=location, include_empty=True)
    # write into template preserving formatting
    out = export_besmm4_using_template(populated, output_path, template_path=template_path)
    print(f"✅ Full BESMM4 BoQ generated: {out}")
    return out

# ----------------- End of module -----------------



