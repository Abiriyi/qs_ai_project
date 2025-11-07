# boq_generator.py
"""
BESMM4-compliant BoQ generator
------------------------------
This script:
1. Loads a BESMM4 CSV template (e.g. qs_ai_project/besmm4_template.csv)
2. Populates quantities from parsed BoQ entries (from drawings)
3. Looks up rates via ai_pricing.get_rate_from_library()
4. Calculates total amounts
5. Exports to formatted Excel (.xlsx)
"""

import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
from collections import defaultdict
from ai_pricing import get_rate_from_library


# ---------------------------------------------
# SETTINGS
# ---------------------------------------------
WORKSECTIONS_ORDER = [
    "Preliminaries",
    "Substructure",
    "Superstructure",
    "Finishes",
    "Fittings & Fixtures",
    "Mechanical & Electrical Works",
    "External Works",
    "Provisional & Prime Cost Sums",
]

DEFAULT_RATE = 0.0


# ---------------------------------------------
# TEMPLATE LOADING
# ---------------------------------------------
def _load_template(template_path: str) -> pd.DataFrame:
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"BESMM4 template not found: {template_path}")

    df = pd.read_csv(template_path)
    df.columns = [c.strip() for c in df.columns]

    expected = ["Section", "Code", "Description", "Unit", "Element"]
    for e in expected:
        if e not in df.columns:
            raise ValueError(f"Missing column in template CSV: {e}")

    df["Quantity"] = 0.0
    df["Rate"] = 0.0
    df["Amount"] = 0.0
    return df


# ---------------------------------------------
# QUANTITY POPULATION LOGIC
# ---------------------------------------------
def populate_template_with_quantities(template_df, parsed_entries, location="Kaduna"):
    """
    Merge parsed quantities into the BESMM4 template.
    """
    if not isinstance(template_df, pd.DataFrame):
        try:
            template_df = pd.DataFrame(template_df)
        except Exception as e:
            print(f"⚠️ Could not convert template to DataFrame: {e}")
            return template_df

    # Aggregate quantities by element name
    quantities_by_element = defaultdict(float)
    for entry in parsed_entries:
        element = str(entry.get("Element") or "").strip().lower()
        qty = float(entry.get("Quantity") or 0)
        if element:
            quantities_by_element[element] += qty

    # Update template quantities and get rates
    for idx, row in template_df.iterrows():
        desc = str(row.get("Description") or "").lower()
        element = str(row.get("Element") or "").lower()
        matched_qty = 0.0

        # Match if element name or description overlap
        for elem, qty in quantities_by_element.items():
            if elem in desc or elem in element:
                matched_qty = qty
                break

        # Assign matched quantity
        template_df.at[idx, "Quantity"] = round(matched_qty, 2)

        # Look up rate
        rate = get_rate_from_library(row.get("Element", ""), row.get("Description", ""), row.get("Unit", ""), location)
        if rate is None:
            rate = DEFAULT_RATE

        template_df.at[idx, "Rate"] = rate
        template_df.at[idx, "Amount"] = round(matched_qty * rate, 2)

    return template_df


# ---------------------------------------------
# EXCEL EXPORT
# ---------------------------------------------
def export_besmm4_excel(populated_df: pd.DataFrame, output_path: str):
    wb = Workbook()
    ws = wb.active
    ws.title = "BESMM4 BoQ"

    # Styles
    currency_fmt = NamedStyle(name="currency_fmt", number_format='"₦"#,##0.00')
    qty_fmt = NamedStyle(name="qty_fmt", number_format="#,##0.##")

    headers = ["Code", "Description", "Unit", "Quantity", "Rate (₦)", "Amount (₦)"]
    ws.append(headers)
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    current_section = None
    row_idx = 2

    # Group rows by Section
    grouped = populated_df.groupby("Section", sort=False)

    for section, group in grouped:
        ws.merge_cells(start_row=row_idx, start_column=2, end_row=row_idx, end_column=6)
        sec_cell = ws.cell(row=row_idx, column=2, value=section)
        sec_cell.font = Font(bold=True, size=12)
        sec_cell.alignment = Alignment(horizontal="left")
        row_idx += 1

        # Write each item under section
        for _, r in group.iterrows():
            ws.cell(row=row_idx, column=1, value=r["Code"])
            ws.cell(row=row_idx, column=2, value=r["Description"])
            ws.cell(row=row_idx, column=3, value=r["Unit"])

            qcell = ws.cell(row=row_idx, column=4, value=r["Quantity"])
            qcell.style = qty_fmt
            qcell.alignment = Alignment(horizontal="right")

            rcell = ws.cell(row=row_idx, column=5, value=r["Rate"])
            rcell.style = currency_fmt
            rcell.alignment = Alignment(horizontal="right")

            acell = ws.cell(row=row_idx, column=6, value=r["Amount"])
            acell.style = currency_fmt
            acell.alignment = Alignment(horizontal="right")

            row_idx += 1

        # Section subtotal
        ws.merge_cells(start_row=row_idx, start_column=2, end_row=row_idx, end_column=5)
        cell = ws.cell(row=row_idx, column=2, value=f"To Collection ({section})")
        cell.font = Font(italic=True)
        ws.cell(row=row_idx, column=6, value=sum(group["Amount"]))
        row_idx += 1

    # Add Summary sheet
    ws_sum = wb.create_sheet("Summary")
    ws_sum.append(["Work Section", "Total (₦)"])
    for col in range(1, 3):
        c = ws_sum.cell(row=1, column=col)
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center")

    totals = populated_df.groupby("Section")["Amount"].sum()
    r = 2
    grand_total = 0.0
    for sec, val in totals.items():
        ws_sum.cell(row=r, column=1, value=sec)
        ws_sum.cell(row=r, column=2, value=round(val, 2)).style = currency_fmt
        grand_total += val
        r += 1

    ws_sum.cell(row=r, column=1, value="GRAND TOTAL").font = Font(bold=True, size=12)
    ws_sum.cell(row=r, column=2, value=round(grand_total, 2)).style = currency_fmt

    # Adjust column widths
    for col in range(1, 7):
        ws.column_dimensions[get_column_letter(col)].width = 20

    wb.save(output_path)
    print(f"✅ BESMM4 BoQ exported: {output_path}")


# ---------------------------------------------
# MAIN GENERATION ENTRYPOINT
# ---------------------------------------------
def generate_besmm4_boq(parsed_entries, template_path, output_path, location="Kaduna"):
    tpl = _load_template(template_path)
    populated = populate_template_with_quantities(tpl, parsed_entries, location=location)
    export_besmm4_excel(populated, output_path)


# ---------------------------------------------
# TEST (optional)
# ---------------------------------------------
if __name__ == "__main__":
    sample_entries = [
        {"Room": "Living Room", "Element": "Blockwork", "Description": "Wall blockwork 225mm thick", "Unit": "m2", "Quantity": 120},
        {"Room": "Living Room", "Element": "Plastering", "Description": "Internal plaster 12mm thick", "Unit": "m2", "Quantity": 240},
        {"Room": "Kitchen", "Element": "Tiling", "Description": "Floor tiling", "Unit": "m2", "Quantity": 12},
    ]

    tpl_path = os.path.join(os.getcwd(), "qs_ai_project", "besmm4_template.csv")
    out_path = os.path.join(os.getcwd(), "qs_ai_project", "besmm4_boq.xlsx")

    generate_besmm4_boq(sample_entries, tpl_path, out_path, location="Kaduna")


