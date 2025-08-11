import pandas as pd
from ai_pricing import get_rate_from_library, get_rate_from_ai

USE_AI = True  # set to False to skip AI pricing

EXCLUDE_TERMS = ["residential", "development"]

TRADE_MAP = {
    "Floor Finish": "Finishes",
    "Wall Finish": "Finishes",
    "Ceiling Finish": "Finishes",
    "Skirting": "Finishes",
    # Later: Add MEP, Joinery, Structural, etc.
}

def generate_boq_excel(boq_entries, output_path, location):
    rows = []
    
    for entry in boq_entries:
        if any(term.lower() in entry.get("Room", "").lower() for term in EXCLUDE_TERMS):
            continue

        trade_section = TRADE_MAP.get(entry.get("Element", ""), "General Works")
        
        # Try library first
        rate = get_rate_from_library(entry.get("Element", ""), entry.get("Description", ""), entry.get("Unit", ""))
        
        # If no rate and AI is enabled
        if rate is None and USE_AI:
            rate = get_rate_from_ai(entry.get("Element", ""), entry.get("Description", ""), entry.get("Unit", ""), location)

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

    df = pd.DataFrame(rows)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="BoQ")

    print(f"✅ BoQ Excel exported to: {output_path}")
