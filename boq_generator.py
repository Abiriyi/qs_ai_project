# boq_generator.py
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
from ai_pricing import get_rate_from_library, get_rate_from_ai

# Words to filter out from room names
EXCLUDE_TERMS = ["residential", "development"]

# Map BoQ elements to BESMM4 work sections
TRADE_MAP = {
    "Floor Finish": "Finishes",
    "Wall Finish": "Finishes",
    "Ceiling Finish": "Finishes",
    "Skirting": "Finishes",
    # Later: Add MEP, Joinery, Structural, etc.
}

# Plural forms for top-level WorkSections
WORKSECTION_PLURAL_MAP = {
    "Finish": "Finishes",
    "Finishes": "Finishes",
    "General Work": "General Works",
    "General Works": "General Works",
    "Structure": "Structures",
    "Substructure": "Substructures"
}

# Plural forms for sub-sections
SUBSECTION_PLURAL_MAP = {
    "Floor Finish": "Floor Finishes",
    "Wall Finish": "Wall Finishes",
    "Ceiling Finish": "Ceiling Finishes",
    "Skirting": "Skirtings"
}

# Default fallback rates if library + AI fail
DEFAULT_RATES = {
    "Floor Finish": 15000,
    "Wall Finish": 12000,
    "Ceiling Finish": 10000,
    "Skirting": 2500,
}

def prepare_boq_entries(boq_entries, location):
    """Process raw boq_entries, clean descriptions, add rates & amounts, and merge duplicates."""
    merged = {}

    for entry in boq_entries:
        # Skip unwanted items
        if any(term.lower() in entry.get("Room", "").lower() for term in EXCLUDE_TERMS):
            continue

        trade_section = TRADE_MAP.get(entry.get("Element", ""), "General Works")
        trade_section = WORKSECTION_PLURAL_MAP.get(trade_section, trade_section)  # pluralize

        element = entry.get("Element", "")
        subsection = SUBSECTION_PLURAL_MAP.get(element, element)  # pluralize

        description = entry.get("Description", "")
        unit = entry.get("Unit", "")
        qty = entry.get("Quantity", 0)

        # 🔹 Remove room names from description
        room_name = entry.get("Room", "")
        if room_name:
            description = description.replace(f" to {room_name}", "")
            description = description.replace(f" in {room_name}", "")
        description = description.strip()

        # Step 1 — Try library rates
        rate = get_rate_from_library(element, description, unit)
        if rate is None:
            rate = get_rate_from_ai(element, description, unit, location)
        if rate is None:
            rate = DEFAULT_RATES.get(element, 0)

        # 🔹 Use a composite key to detect duplicates
        key = (trade_section, element, description, unit, rate)

        if key not in merged:
            merged[key] = {
                "WorkSection": trade_section,
                "SubSection": subsection,
                "Description": description,
                "Unit": unit,
                "Qty": qty,
                "Rate": rate,
                "Amount": round(rate * qty, 2) if rate else 0
            }
        else:
            # Sum up quantities and recalc amount
            merged[key]["Qty"] += qty
            merged[key]["Amount"] = round(merged[key]["Rate"] * merged[key]["Qty"], 2)

    # Convert dict back to list
    return list(merged.values())

def generate_boq_excel(boq_entries, output_path, location, mode="plain"):
    """
    Generate a BoQ in Excel format.
    mode = "plain"  -> structured table (no merged cells)
    mode = "styled" -> mirror of PDF template (with headers merged + bold)
    """
    processed_entries = prepare_boq_entries(boq_entries, location)

    if mode == "plain":
        df = pd.DataFrame(processed_entries)
        df.insert(0, "Item", [chr(65 + i) for i in range(len(df))])
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="BoQ")

    elif mode == "styled":
        wb = Workbook()
        ws = wb.active
        ws.title = "BoQ"

        # Styles
        currency_fmt = NamedStyle(name="currency_fmt", number_format='"₦"#,##0.00')
        qty_fmt = NamedStyle(name="qty_fmt", number_format="#,##0.##")

        # Header row
        headers = ["Item", "Description", "Unit", "Qty", "Rate (₦)", "Amount (₦)"]
        ws.append(headers)
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        row_num = 2
        current_section = None
        current_subsection = None
        item_counter = 0

        for entry in processed_entries:
            section = entry["WorkSection"]
            subsection = entry["SubSection"]

            # Section header
            # Section header
            if section != current_section:
                ws.merge_cells(start_row=row_num, start_column=2, end_row=row_num, end_column=6)  # 👈 shift to col 2
                ws.cell(row=row_num, column=2, value=section).font = Font(bold=True, size=12)
                ws.cell(row=row_num, column=2).alignment = Alignment(horizontal="left")
                row_num += 1
                current_section = section
                current_subsection = None

            # Subsection header
            if subsection != current_subsection:
                ws.merge_cells(start_row=row_num, start_column=2, end_row=row_num, end_column=6)  # 👈 shift to col 2
                ws.cell(row=row_num, column=2, value=subsection).font = Font(bold=True, italic=True)
                ws.cell(row=row_num, column=2).alignment = Alignment(horizontal="left")
                row_num += 1
                current_subsection = subsection

            # Item row
            item_counter += 1
            ws.cell(row=row_num, column=1, value=chr(64 + item_counter))
            ws.cell(row=row_num, column=2, value=entry["Description"])
            ws.cell(row=row_num, column=3, value=entry["Unit"])

            qty_cell = ws.cell(row=row_num, column=4, value=entry["Qty"])
            qty_cell.style = qty_fmt
            qty_cell.alignment = Alignment(horizontal="right")

            rate_cell = ws.cell(row=row_num, column=5, value=entry["Rate"])
            rate_cell.style = currency_fmt
            rate_cell.alignment = Alignment(horizontal="right")

            amt_cell = ws.cell(row=row_num, column=6, value=entry["Amount"])
            amt_cell.style = currency_fmt
            amt_cell.alignment = Alignment(horizontal="right")

            row_num += 1

        # Adjust column widths
        for col in range(1, 7):
            col_letter = get_column_letter(col)
            ws.column_dimensions[col_letter].width = 18 if col > 2 else 30

        wb.save(output_path)

    else:
        raise ValueError("mode must be either 'plain' or 'styled'")

    print(f"✅ BoQ Excel exported to: {output_path} ({mode} mode)")


