# boq_generator.py
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, NamedStyle
from openpyxl.utils import get_column_letter
from ai_pricing import get_rate_from_library, get_rate_from_ai

# Words to filter out from room names
EXCLUDE_TERMS = ["residential", "development"]

# Map BoQ elements to BESMM4 work sections
# Map BoQ elements to BESMM4 / trade work sections
TRADE_MAP = {
    # 1. Preliminaries
    "Site Establishment": "Preliminaries",
    "Temporary Works": "Preliminaries",
    "Site Management": "Preliminaries",

    # 2. Substructure Works
    "Site Clearance": "Substructure Works",
    "Excavation": "Substructure Works",
    "Earthworks": "Substructure Works",
    "Foundations": "Substructure Works",
    "Basement": "Substructure Works",
    "Ground Floor Slab": "Substructure Works",

    # 3. Superstructure Works
    # a. Concrete Work
    "Concrete": "Superstructure Works",
    "Reinforced Concrete": "Superstructure Works",

    # b. Masonry / Blockwork
    "Masonry": "Superstructure Works",
    "Blockwork": "Superstructure Works",
    "Partition Walls": "Superstructure Works",

    # c. Structural Steelwork
    "Steelwork": "Superstructure Works",
    "Structural Steel": "Superstructure Works",
    "Roof Trusses": "Superstructure Works",

    # d. Roofing
    "Roof Structure": "Superstructure Works",
    "Roof Coverings": "Superstructure Works",

    # e. Carpentry & Joinery
    "Carpentry": "Superstructure Works",
    "Joinery": "Superstructure Works",
    "Doors": "Superstructure Works",
    "Windows": "Superstructure Works",
    "Frames": "Superstructure Works",
    "Skirting": "Superstructure Works",

    # 4. Finishes
    "Plastering": "Finishes",
    "Screeding": "Finishes",
    "Tiling": "Finishes",
    "Painting": "Finishes",
    "Decoration": "Finishes",
    "Floor Finish": "Finishes",
    "Wall Finish": "Finishes",
    "Ceiling Finish": "Finishes",

    # 5. Fittings & Fixtures
    "Ironmongery": "Fittings & Fixtures",
    "Cabinets": "Fittings & Fixtures",
    "Wardrobes": "Fittings & Fixtures",
    "Shelves": "Fittings & Fixtures",
    "Sanitary Fittings": "Fittings & Fixtures",
    "Kitchen Fittings": "Fittings & Fixtures",

    # 6. Mechanical & Electrical Works (MEP)
    # a. Mechanical
    "Plumbing": "Mechanical & Electrical Works",
    "Drainage": "Mechanical & Electrical Works",
    "Sanitary Installations": "Mechanical & Electrical Works",
    "HVAC": "Mechanical & Electrical Works",
    "Fire Protection": "Mechanical & Electrical Works",

    # b. Electrical
    "Power Supply": "Mechanical & Electrical Works",
    "Lighting": "Mechanical & Electrical Works",
    "Small Power": "Mechanical & Electrical Works",
    "Data": "Mechanical & Electrical Works",
    "Telecom": "Mechanical & Electrical Works",
    "CCTV": "Mechanical & Electrical Works",
    "Alarms": "Mechanical & Electrical Works",
    "Lightning Protection": "Mechanical & Electrical Works",

    # 7. External Works
    "Paving": "External Works",
    "Driveways": "External Works",
    "Car Parks": "External Works",
    "Boundary Walls": "External Works",
    "Gates": "External Works",
    "Landscaping": "External Works",
    "Surface Water Drainage": "External Works",
    "External Services": "External Works",

    # 8. Provisional & Prime Cost Sums
    "Specialized Works": "Provisional & Prime Cost Sums",
    "Contingencies": "Provisional & Prime Cost Sums",
}

# Plural forms for top-level WorkSections
WORKSECTION_PLURAL_MAP = {
    "Finish": "Finishes",
    "Finishes": "Finishes",
    "General Work": "General Works",
    "General Works": "General Works",
    "Structure": "Structures",
    "Structures": "Structures",
    "Substructure": "Substructures",
    "Substructures": "Substructures",
    "Substructure Works": "Substructure Works",
    "Superstructure Works": "Superstructure Works",
    "External Work": "External Works",
    "External Works": "External Works",
    "Services": "Services",
    "Preliminaries": "Preliminaries"
}

SUBSECTION_PLURAL_MAP = {
    "Floor Finish": "Floor Finishes",
    "Wall Finish": "Wall Finishes",
    "Ceiling Finish": "Ceiling Finishes",
    "Skirting": "Skirtings",
    "Painting": "Paintings",
    "Plaster": "Plasters",
    "Door Finish": "Door Finishes",
    "Window Finish": "Window Finishes",
    "Mechanical Service": "Mechanical Services",
    "Electrical Service": "Electrical Services",
    "Plumbing Service": "Plumbing Services"
}

def pluralize_worksection(name: str) -> str:
    """Return plural form of worksection or 'Unclassified' if missing."""
    return WORKSECTION_PLURAL_MAP.get(name, "Unclassified")

def pluralize_subsection(name: str) -> str:
    """Return plural form of subsection or original if not mapped."""
    return SUBSECTION_PLURAL_MAP.get(name, name)

def generate_boq(items: list[dict]) -> dict:
    boq = {}
    for item in items:
        worksection = pluralize_worksection(item.get("worksection", ""))
        subsection = pluralize_subsection(item.get("subsection", ""))
        
        boq.setdefault(worksection, {})
        boq[worksection].setdefault(subsection, [])
        boq[worksection][subsection].append(item)
    
    return boq

# Ordered list of QS Work Sections for summary
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

# Default fallback rates if library + AI fail (₦ per unit)
DEFAULT_RATES = {
    # 1. Preliminaries
    "Site Establishment": 500000,        # lump sum
    "Temporary Works": 300000,
    "Site Management": 400000,

    # 2. Substructure Works
    "Site Clearance": 1500,              # per m²
    "Excavation": 2000,                  # per m³
    "Earthworks": 2500,                  # per m³
    "Foundations": 30000,                # per m³ concrete
    "Basement": 50000,                   # per m³
    "Ground Floor Slab": 35000,          # per m²

    # 3. Superstructure Works
    # a. Concrete Work
    "Concrete": 30000,                   # per m³
    "Reinforced Concrete": 40000,        # per m³

    # b. Masonry / Blockwork
    "Masonry": 8000,                     # per m²
    "Blockwork": 7000,                   # per m²
    "Partition Walls": 6000,             # per m²

    # c. Structural Steelwork
    "Steelwork": 50000,                  # per tonne
    "Structural Steel": 55000,           # per tonne
    "Roof Trusses": 20000,               # per m² plan area

    # d. Roofing
    "Roof Structure": 25000,             # per m²
    "Roof Coverings": 20000,             # per m²

    # e. Carpentry & Joinery
    "Carpentry": 15000,                  # per m² or lump sum
    "Joinery": 12000,
    "Doors": 45000,                      # per door
    "Windows": 40000,                    # per window
    "Frames": 10000,                     # per m
    "Skirting": 2500,                    # per m

    # 4. Finishes
    "Plastering": 12000,                 # per m²
    "Screeding": 11000,                  # per m²
    "Tiling": 15000,                     # per m²
    "Painting": 8000,                    # per m²
    "Decoration": 10000,                 # per m²
    "Floor Finish": 15000,               # per m²
    "Wall Finish": 12000,                # per m²
    "Ceiling Finish": 10000,             # per m²

    # 5. Fittings & Fixtures
    "Ironmongery": 5000,                 # per set
    "Cabinets": 80000,                   # per cabinet
    "Wardrobes": 100000,                 # per wardrobe
    "Shelves": 15000,                    # per shelf
    "Sanitary Fittings": 60000,          # per fitting
    "Kitchen Fittings": 120000,          # per kitchen set

    # 6. Mechanical & Electrical Works (MEP)
    # a. Mechanical
    "Plumbing": 20000,                   # per point
    "Drainage": 15000,                   # per point
    "Sanitary Installations": 50000,     # per fitting
    "HVAC": 300000,                      # per system unit
    "Fire Protection": 100000,           # per installation

    # b. Electrical
    "Power Supply": 80000,               # per panel
    "Lighting": 5000,                    # per fitting
    "Small Power": 4000,                 # per point
    "Data": 6000,                        # per point
    "Telecom": 8000,                     # per point
    "CCTV": 15000,                       # per camera
    "Alarms": 20000,                     # per point
    "Lightning Protection": 50000,       # per system

    # 7. External Works
    "Paving": 12000,                     # per m²
    "Driveways": 15000,                  # per m²
    "Car Parks": 14000,                  # per m²
    "Boundary Walls": 20000,             # per m²
    "Gates": 80000,                      # per gate
    "Landscaping": 1000,                 # per m²
    "Surface Water Drainage": 5000,      # per m
    "External Services": 50000,          # per connection

    # 8. Provisional & Prime Cost Sums
    "Specialized Works": 1000000,        # lump sum
    "Contingencies": 500000,             # lump sum
}

def prepare_boq_entries(boq_entries, location):
    """Process raw boq_entries, clean descriptions, add rates & amounts, and merge duplicates."""
    merged = {}

    for entry in boq_entries:
        # Skip unwanted items
        if any(term.lower() in entry.get("Room", "").lower() for term in EXCLUDE_TERMS):
            continue

        trade_section = TRADE_MAP.get(entry.get("Element", ""), "General Works")
        trade_section = pluralize_worksection(trade_section)

        element = entry.get("Element", "")
        subsection = pluralize_subsection(element)

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

        # --- Create Summary Sheet ---
        ws_summary = wb.create_sheet(title="Summary")

        # Headers
        headers = ["Work Section", "Total (₦)"]
        ws_summary.append(headers)
        for col in range(1, 3):
            cell = ws_summary.cell(row=1, column=col)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        # Calculate totals per section
        section_totals = {}
        grand_total = 0
        for entry in processed_entries:
            section = entry["WorkSection"].upper()
            amount = entry["Amount"] or 0
            section_totals[section] = section_totals.get(section, 0) + amount
            grand_total += amount

        # Write section totals in QS order (only if non-zero)
        row_num = 2
        for section in WORKSECTIONS_ORDER:
                total = section_totals.get(section.upper(), 0)
                if total > 0:
                    ws_summary.cell(row=row_num, column=1, value=section).font = Font(bold=True)
                amt_cell = ws_summary.cell(row=row_num, column=2, value=total)
                amt_cell.style = currency_fmt
                amt_cell.alignment = Alignment(horizontal="right")
                row_num += 1

        # GRAND TOTAL
        ws_summary.cell(row=row_num,column=1, value="GRAND TOTAL").font = Font(bold=True, size=12)
        amt_cell = ws_summary.cell(row=row_num, column=2, value=grand_total)
        amt_cell.style = currency_fmt
        amt_cell.alignment = Alignment(horizontal="right")
        amt_cell.font = Font(bold=True, size=12)

        # Save workbook
        wb.save(output_path)

    else:
        raise ValueError("mode must be either 'plain' or 'styled'")

    print(f"✅ BoQ Excel exported to: {output_path} ({mode} mode)")


