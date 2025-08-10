import pandas as pd
import pdfplumber
from parse_section import get_wall_finish
from ai_pricing import get_rate_from_library, get_rate_from_ai

use_ai = True  # Set to False to skip AI and only use local rates

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

def build_boq_entries(rooms):
    boq_entries = []
    for room in rooms:
        room_name = room["Room"]
        area = room["Area"]
        perimeter = room["Perimeter"]

        # Floor finish
        boq_entries.append({
            "Room": room_name,
            "Element": "Floor Finish",
            "Description": f"600x600mm ceramic tiles laid to floor in {room_name}",
            "Quantity": round(area, 2),
            "Unit": "m²"
        })

        # Wall finish (example: paint)
        boq_entries.append({
            "Room": room_name,
            "Element": "Wall Finish",
            "Description": f"Emulsion paint on walls in {room_name}",
            "Quantity": round(perimeter * 2.8, 2),  # assuming 2.8m height
            "Unit": "m²"
        })

        # Ceiling finish
        boq_entries.append({
            "Room": room_name,
            "Element": "Ceiling Finish",
            "Description": f"P.O.P suspended ceiling in {room_name}",
            "Quantity": round(area, 2),
            "Unit": "m²"
        })

        # Skirting
        boq_entries.append({
            "Room": room_name,
            "Element": "Skirting",
            "Description": f"100mm high ceramic tile skirting in {room_name}",
            "Quantity": round(perimeter, 2),
            "Unit": "m"
        })

    return boq_entries

def generate_boq_excel(boq_entries, output_path, location="Abuja"):
    rows = []
    for entry in boq_entries:
        # Skip unwanted items
        if any(term.lower() in entry.get("Room", "").lower() for term in EXCLUDE_TERMS):
            continue
        if entry["Element"] not in TRADE_MAP:
            continue
        trade_section = TRADE_MAP.get(entry["Element"], "General Works")

        # 1. Try local rate library
        rate = get_rate_from_library(entry["Element"], entry["Description"], entry["Unit"], location)

        # 2. If not found and AI enabled, call AI
        if rate is None and use_ai:
            rate = get_rate_from_ai(entry["Element"], entry["Description"], entry["Unit"], location)

        amount = round(rate * entry["Quantity"], 2) if rate else ""

        rows.append({
            "BESMM4 Work Sections Master Bill": trade_section,
            "Description": entry["Description"],
            "Qty": entry["Quantity"],
            "Unit": entry["Unit"],
            "Rate": rate if rate else "",
            "Amount": amount
        })

    df = pd.DataFrame(rows)

    # Save in template style
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet 1")