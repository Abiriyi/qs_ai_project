# boq_generator.py
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
from ai_pricing import get_rate_from_library, get_rate_from_ai

# ===========================
# 🔹 Configuration
# ===========================
EXCLUDE_TERMS = ["residential", "development"]

WORKSECTIONS_ORDER = [
    "Preliminaries",
    "Substructure Works",
    "Superstructure Works",
    "Finishes",
    "Fittings & Fixtures",
    "Mechanical & Electrical Works",
    "External Works",
    "Provisional & Prime Cost Sums"
]

# Default fallback rates (₦ per unit)
DEFAULT_RATES = {
    "Excavation": 2000,
    "Blockwork": 8000,
    "Concrete": 30000,
    "Painting": 8000,
    "Plastering": 12000,
    "Doors": 45000,
    "Windows": 40000,
    "Floor Finish": 15000,
    "Tiling": 15000,
    "Screeding": 11000,
    "Paving": 12000,
    "Roof Coverings": 20000,
    "Plumbing": 20000,
    "Lighting": 5000,
    "Sanitary Fittings": 60000,
}

TRADE_MAP = {
    "Site Clearance": "Substructure Works",
    "Excavation": "Substructure Works",
    "Concrete": "Superstructure Works",
    "Blockwork": "Superstructure Works",
    "Plastering": "Finishes",
    "Painting": "Finishes",
    "Tiling": "Finishes",
    "Doors": "Superstructure Works",
    "Windows": "Superstructure Works",
    "Floor Finish": "Finishes",
    "Roof Coverings": "Superstructure Works",
    "Lighting": "Mechanical & Electrical Works",
    "Plumbing": "Mechanical & Electrical Works",
    "Sanitary Fittings": "Fittings & Fixtures",
    "Paving": "External Works",
}

def pluralize_worksection(name: str) -> str:
    return {
        "Preliminary": "Preliminaries",
        "Substructure": "Substructure Works",
        "Superstructure": "Superstructure Works",
        "Finish": "Finishes",
        "External Work": "External Works",
    }.get(name, name)

def pluralize_subsection(name: str) -> str:
    if not name:
        return name
    if "finish" in name.lower():
        return name.title() + "es" if not name.endswith("es") else name.title()
    return name.title()

# ===========================
# 🔹 Prepare & Merge BoQ Entries
# ===========================
def prepare_boq_entries(boq_entries, location):
    merged = {}

    for entry in boq_entries:
        # Skip irrelevant rooms
        if any(term.lower() in str(entry.get("Room", "")).lower() for term in EXCLUDE_TERMS):
            continue

        element = entry.get("Element", "")
        trade_section = TRADE_MAP.get(element, "General Works")
        trade_section = pluralize_worksection(trade_section)
        subsection = pluralize_subsection(element)

        description = entry.get("Description", "").strip()
        unit = entry.get("Unit", "")
        qty = entry.get("Quantity", 0) or 0

        # Step 1: Try CSV rates (Kaduna-based, adjusted for location/year)
        rate = get_rate_from_library(element, description, unit, location)
        if rate:
            source = "📘 CSV"
        else:
            # Step 2: Try AI (if available)
            rate = get_rate_from_ai(element, description, unit, location)
            if rate:
                source = "🤖 AI"
            else:
                # Step 3: Fallback to default
                rate = DEFAULT_RATES.get(element, 0)
                source = "⚙️ Default"

        # Debug output (only first 10 for clarity)
        if len(merged) < 10:
            print(f"➡️ {element}: {rate} ₦/{unit} ({source})")

        key = (trade_section, element, description, unit, rate)
        if key not in merged:
            merged[key] = {
                "WorkSection": trade_section,
                "SubSection": subsection,
                "Description": description,
                "Unit": unit,
                "Qty": qty,
                "Rate": rate,
                "Amount": round(rate * qty, 2),
            }
        else:
            merged[key]["Qty"] += qty
            merged[key]["Amount"] = round(merged[key]["Rate"] * merged[key]["Qty"], 2)

    return list(merged.values())

# ===========================
# 🔹 Excel Export
# ===========================
def generate_boq_excel(boq_entries, output_path, location, mode="plain"):
    processed_entries = prepare_boq_entries(boq_entries, location)

    if not processed_entries:
        print("❌ No BoQ entries to export.")
        return

    if mode == "plain":
        df = pd.DataFrame(processed_entries)
        df.insert(0, "Item", [chr(65 + i) for i in range(len(df))])
        df.to_excel(output_path, index=False, sheet_name="BoQ")
        print(f"✅ Plain Excel exported: {output_path}")
        return

    wb = Workbook()
    ws = wb.active
    ws.title = "BoQ"

    currency_fmt = NamedStyle(name="currency_fmt", number_format='"₦"#,##0.00')
    qty_fmt = NamedStyle(name="qty_fmt", number_format="#,##0.##")

    headers = ["Item", "Description", "Unit", "Qty", "Rate (₦)", "Amount (₦)"]
    ws.append(headers)
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    row = 2
    section = None
    subsection = None
    item_counter = 0

    for entry in processed_entries:
        if entry["WorkSection"] != section:
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
            ws.cell(row=row, column=2, value=entry["WorkSection"]).font = Font(bold=True, size=12)
            row += 1
            section = entry["WorkSection"]
            subsection = None

        if entry["SubSection"] != subsection:
            ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
            ws.cell(row=row, column=2, value=entry["SubSection"]).font = Font(bold=True, italic=True)
            row += 1
            subsection = entry["SubSection"]

        item_counter += 1
        ws.cell(row=row, column=1, value=chr(64 + item_counter))
        ws.cell(row=row, column=2, value=entry["Description"])
        ws.cell(row=row, column=3, value=entry["Unit"])

        q_cell = ws.cell(row=row, column=4, value=entry["Qty"])
        q_cell.style = qty_fmt
        q_cell.alignment = Alignment(horizontal="right")

        r_cell = ws.cell(row=row, column=5, value=entry["Rate"])
        r_cell.style = currency_fmt
        r_cell.alignment = Alignment(horizontal="right")

        a_cell = ws.cell(row=row, column=6, value=entry["Amount"])
        a_cell.style = currency_fmt
        a_cell.alignment = Alignment(horizontal="right")

        row += 1

    for c in range(1, 7):
        ws.column_dimensions[get_column_letter(c)].width = 18 if c > 2 else 30

    # --- Summary Sheet ---
    summary = wb.create_sheet(title="Summary")
    summary.append(["Work Section", "Total (₦)"])
    for col in range(1, 3):
        cell = summary.cell(row=1, column=col)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    section_totals = {}
    total_sum = 0
    for e in processed_entries:
        ws_name = e["WorkSection"].upper()
        amt = e["Amount"]
        section_totals[ws_name] = section_totals.get(ws_name, 0) + amt
        total_sum += amt

    row = 2
    for ws_name in WORKSECTIONS_ORDER:
        total = section_totals.get(ws_name.upper(), 0)
        if total > 0:
            summary.cell(row=row, column=1, value=ws_name).font = Font(bold=True)
        amt_cell = summary.cell(row=row, column=2, value=total)
        amt_cell.style = currency_fmt
        amt_cell.alignment = Alignment(horizontal="right")
        row += 1

    summary.cell(row=row, column=1, value="GRAND TOTAL").font = Font(bold=True, size=12)
    total_cell = summary.cell(row=row, column=2, value=total_sum)
    total_cell.style = currency_fmt
    total_cell.font = Font(bold=True, size=12)
    total_cell.alignment = Alignment(horizontal="right")

    wb.save(output_path)
    print(f"✅ Styled Excel exported: {output_path}")



