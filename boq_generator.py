# boq_generator_full_besmm4.py
"""
Full BESMM4 hierarchical BoQ generator (no CSV/template needed).

Usage:
    from boq_generator_full_besmm4 import generate_besmm4_boq
    generate_besmm4_boq(parsed_entries_list, "output.xlsx", location="Kaduna")

Requires:
    - pandas
    - openpyxl
    - ai_pricing.get_rate_from_library(element, description, unit, location)
"""

import os
from collections import defaultdict, OrderedDict
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
from ai_pricing import get_rate_from_library

# ---------- Config ----------
DEFAULT_RATE = 0.0

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

# Hierarchical structure:
# section_code -> list of groups -> each group is (group_code_suffix, group_name, items_list)
# each item in items_list: (item_code_suffix, short_desc, default_unit, canonical_element_key)
BESMM4_HIERARCHY = {
    "2.0": [  # SUBSTRUCTURE example (full standard would extend)
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
    # Preliminaries can be added similarly under "1.0" if desired
}

# A lightweight keyword mapping to help match parsed elements -> canonical keys in hierarchy
# Lowercase keys map to the canonical element string stored in hierarchy items.
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
    # exact keyword search
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
    Aggregate parsed entries into a dict keyed by canonical element + unit.
    Returns: dict {canonical_str.lower(): {unit: qty, 'descriptions': set(...) } }
    """
    agg = {}
    for e in parsed_entries:
        element = (e.get("Element") or "").strip()
        description = (e.get("Description") or "").strip()
        unit = (e.get("Unit") or "").strip() or "item"
        qty = e.get("Quantity", e.get("Qty", 0)) or 0
        try:
            qty = float(qty)
        except Exception:
            try:
                qty = float(str(qty).replace(",", ""))
            except Exception:
                qty = 0.0

        canonical = _canonical_element_from_text(element) or _canonical_element_from_text(description) or element or description
        if not canonical:
            continue
        key = canonical.lower()
        if key not in agg:
            agg[key] = {"units": defaultdict(float), "descriptions": set()}
        agg[key]["units"][unit] += qty
        if description:
            agg[key]["descriptions"].add(description)
    return agg

# ---------------- Template population ----------------

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
                    "Amount": 0.0
                })
    return items

def populate_besmm4_from_parsed(parsed_entries, location="Kaduna", include_empty=True):
    """
    Map parsed entries into the full BESMM4 item list, fill quantities and rates.
    Returns: pandas.DataFrame of populated items.
    """
    agg = aggregate_parsed_entries(parsed_entries)
    items = _build_full_item_list(include_empty=include_empty)

    # Map aggregated quantities into items
    for it in items:
        key = (it["Canonical"] or it["Description"]).lower()
        qty = 0.0
        # If exact match in agg
        if key in agg:
            # choose the unit matching template if available, else pick any
            units = agg[key]["units"]
            tunit = it["Unit"]
            # try exact unit
            if tunit in units and units[tunit] > 0:
                qty = units[tunit]
            else:
                # pick largest quantity across units as fallback
                if units:
                    qty = max(units.values())
        else:
            # Try fuzzy match (element keywords contained in canonical or desc)
            for agg_key, v in agg.items():
                if agg_key in key or key in agg_key:
                    # pick sum of units
                    qty = sum(v["units"].values())
                    break

        it["Quantity"] = float(round(qty, 4))

        # Rate lookup
        try:
            rate = get_rate_from_library(it["Canonical"], it["Description"], it["Unit"], location=location)
        except Exception:
            rate = None
        if rate is None:
            rate = DEFAULT_RATE
        it["Rate"] = float(rate)
        it["Amount"] = round(it["Quantity"] * it["Rate"], 2)

    df = pd.DataFrame(items)
    return df

# ---------------- Excel export (hierarchical formatting) ----------------

def export_besmm4_excel(populated_df: pd.DataFrame, output_path: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "BESMM4 BoQ"

    # Styles
    qty_fmt = NamedStyle(name="qty_fmt", number_format="#,##0.##")
    currency_fmt = NamedStyle(name="currency_fmt", number_format='"₦"#,##0.00')

    # Avoid duplicate NamedStyle registration in repeated runs
    try:
        wb.add_named_style(qty_fmt)
    except Exception:
        pass
    try:
        wb.add_named_style(currency_fmt)
    except Exception:
        pass

    headers = ["Item Code", "Description", "Unit", "Quantity", "Rate (₦)", "Amount (₦)"]
    ws.append(headers)
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    row = 2
    grand_total = 0.0

    # iterate through sections in order
    for sec_code, sec_name in BESMM4_SECTIONS.items():
        sec_rows = populated_df[populated_df["SectionCode"] == sec_code]
        if sec_rows.empty:
            continue

        # Section header
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        sh = ws.cell(row=row, column=1, value=f"{sec_code} {sec_name}")
        sh.font = Font(bold=True, size=12)
        row += 1

        # group by group code
        group_codes = sec_rows["GroupCode"].unique().tolist()
        for g_code in group_codes:
            g_rows = sec_rows[sec_rows["GroupCode"] == g_code]
            if g_rows.empty:
                continue
            g_name = g_rows.iloc[0]["GroupName"]
            # Group header (italic)
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
            gh = ws.cell(row=row, column=1, value=f"{g_code} {g_name}")
            gh.font = Font(italic=True, size=11)
            row += 1

            # Items
            for _, r in g_rows.iterrows():
                ws.cell(row=row, column=1, value=r["ItemCode"])
                ws.cell(row=row, column=2, value=r["Description"])
                ws.cell(row=row, column=3, value=r["Unit"])

                qcell = ws.cell(row=row, column=4, value=r["Quantity"])
                qcell.style = qty_fmt
                qcell.alignment = Alignment(horizontal="right")

                rcell = ws.cell(row=row, column=5, value=r["Rate"])
                rcell.style = currency_fmt
                rcell.alignment = Alignment(horizontal="right")

                acell = ws.cell(row=row, column=6, value=r["Amount"])
                acell.style = currency_fmt
                acell.alignment = Alignment(horizontal="right")

                row += 1

            # Subtotal for group
            group_total = round(g_rows["Amount"].sum(), 2)
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
            st = ws.cell(row=row, column=1, value=f"To Collection ({g_code} {g_name})")
            st.font = Font(italic=True)
            st.alignment = Alignment(horizontal="left")
            subtotal_cell = ws.cell(row=row, column=6, value=group_total)
            subtotal_cell.style = currency_fmt
            subtotal_cell.alignment = Alignment(horizontal="right")
            row += 2

            grand_total += group_total

    # Grand total row
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
    gt_cell = ws.cell(row=row, column=1, value="GRAND TOTAL")
    gt_cell.font = Font(bold=True, size=12)
    gt_amt = ws.cell(row=row, column=6, value=round(grand_total, 2))
    gt_amt.style = currency_fmt
    gt_amt.alignment = Alignment(horizontal="right")

    # Adjust widths
    widths = [14, 60, 10, 14, 16, 18]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Save
    wb.save(output_path)
    return output_path

# ---------------- Public entrypoint ----------------

def generate_besmm4_boq(parsed_entries: list[dict], output_path: str, location: str = "Kaduna"):
    """
    High-level function:
      - parsed_entries: list of dicts with keys Room, Element, Description, Unit, Quantity
      - output_path: path to .xlsx to write
      - location: passed to rate lookup
    """
    if not isinstance(parsed_entries, list):
        raise ValueError("parsed_entries must be a list of dicts")

    populated = populate_besmm4_from_parsed(parsed_entries, location=location, include_empty=True)
    export_besmm4_excel(populated, output_path)
    print(f"✅ Full BESMM4 BoQ generated: {output_path}")
    return output_path


# ----------------- End of module -----------------



