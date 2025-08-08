import pandas as pd
from parse_section import get_wall_finish

EXCLUDE_TERMS = ["residential", "development"]

def generate_boq_excel(room_data, output_path="boq_output.xlsx"):
    boq_entries = []

    for room in room_data:
        name = room["room"].lower()
        if any(term in name for term in EXCLUDE_TERMS):
            continue  # skip metadata text

        if not room["area_m2"]:
            continue  # skip if area couldn't be computed

        room_name = room["room"]
        area = room["area_m2"]
        length = room["length_mm"] / 1000  # convert to meters
        width = room["width_mm"] / 1000

        # Floor finish
        boq_entries.append({
            "Room": room_name,
            "Element": "Floor Finish",
            "Description": "600x600mm ceramic tiles laid to floor",
            "Unit": "m²",
            "Quantity": round(area, 2)
        })

        # Wall finish
        wall_type, height_mm = get_wall_finish(room_name)
        perimeter = 2 * (length + width)
        wall_area = round(perimeter * (height_mm / 1000), 2)

        boq_entries.append({
            "Room": room_name,
            "Element": "Wall Finish",
            "Description": wall_type,
            "Unit": "m²",
            "Quantity": wall_area
        })
        
        # Ceiling finish
        boq_entries.append({
            "Room": room_name,
            "Element": "Ceiling Finish",
            "Description": "Gypsum board ceiling",
            "Unit": "m²",
            "Quantity": round(area, 2)
        })

    df = pd.DataFrame(boq_entries)
    df.to_excel(output_path, index=False)
    print(f"✅ BoQ Excel exported to: {output_path}")
