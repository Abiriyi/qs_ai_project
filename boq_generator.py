import pandas as pd
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

def generate_boq_excel(boq_entries, output_path, location):
    """
    Generate a priced BoQ in Excel format.
    boq_entries: list of dicts with Room, Element, Description, Quantity, Unit
    """
    rows = []
    
    for entry in boq_entries:
        # Skip unwanted items
        if any(term.lower() in entry.get("Room", "").lower() for term in EXCLUDE_TERMS):
            continue

        trade_section = TRADE_MAP.get(entry.get("Element", ""), "General Works")
        
        # Step 1 — Try library rates first
        rate = get_rate_from_library(entry.get("Element", ""), entry.get("Description", ""), entry.get("Unit", ""))
        
        # Step 2 — If not found, try AI pricing
        if rate is None:
            rate = get_rate_from_ai(entry.get("Element", ""), entry.get("Description", ""), entry.get("Unit", ""), location)

        # Step 3 — Calculate amount
        amount = round(rate * entry.get("Quantity", 0), 2) if rate else ""

        rows.append({
            "BESMM4 Work Sections Master Bill": trade_section,
            "Room": entry.get("Room", ""),
            "Description": entry.get("Description", ""),
            "Qty": entry.get("Quantity", ""),
            "Unit": entry.get("Unit", ""),
            "Rate": rate if rate else "",
            "Amount": amount
        })

    # Create DataFrame and save to Excel
    df = pd.DataFrame(rows)

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="BoQ")

    print(f"✅ BoQ Excel exported to: {output_path}")
