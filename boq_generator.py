import pandas as pd

EXCLUDE_TERMS = ["residential", "development"]

def generate_boq_excel(room_data, output_path="boq_output.xlsx"):
    boq_entries = []

    for room in room_data:
        name = room["room"].lower()
        if any(term in name for term in EXCLUDE_TERMS):
            continue  # skip metadata text

        if not room["area_m2"]:
            continue  # skip if area couldn't be computed

        boq_entries.append({
            "Room": room["room"],
            "Element": "Floor Finish",
            "Description": "600x600mm ceramic tiles laid to floor",
            "Unit": "m²",
            "Quantity": room["area_m2"]
        })

    df = pd.DataFrame(boq_entries)
    df.to_excel(output_path, index=False)
    print(f"✅ BoQ Excel exported to: {output_path}")
