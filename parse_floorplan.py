# parse_floorplan.py
from pdf_parser import extract_pdf_text
import math

def parse_floorplan(pdf_path, location="Lagos"):
    """
    Parse the floorplan PDF into structured BoQ entries.
    - Uses per-room dimensions & heights
    - Deducts openings (doors, windows)
    """
    pdf_data = extract_pdf_text(pdf_path)
    rooms = pdf_data["rooms"]
    openings = pdf_data["openings"]

    boq_entries = []

    for room in rooms:
        room_name = room.get("Room", "Unknown")
        length = room.get("Length")
        width = room.get("Width")
        height = room.get("Height", 3.0)
        area = room.get("Area")
        perimeter = room.get("Perimeter")

        # Skip if no dimensions were found
        if not area or not perimeter:
            continue

        # --- Calculate total opening area for this room ---
        opening_area = 0
        for o in openings:
            if o["width_m"] and o["height_m"]:
                opening_area += o["count"] * o["width_m"] * o["height_m"]

        # --- Floor finishes ---
        boq_entries.append({
            "Room": room_name,
            "Element": "Floor Finish",
            "Description": f"Floor finish to {room_name}",
            "Unit": "m²",
            "Quantity": round(area, 2)
        })

        # --- Wall finishes (net of openings) ---
        wall_area = max(perimeter * height - opening_area, 0)
        boq_entries.append({
            "Room": room_name,
            "Element": "Wall Finish",
            "Description": f"Wall finish to {room_name}",
            "Unit": "m²",
            "Quantity": round(wall_area, 2)
        })

        # --- Ceiling finishes (same as floor area) ---
        boq_entries.append({
            "Room": room_name,
            "Element": "Ceiling Finish",
            "Description": f"Ceiling finish to {room_name}",
            "Unit": "m²",
            "Quantity": round(area, 2)
        })

        # --- Skirting (assume perimeter skirting) ---
        boq_entries.append({
            "Room": room_name,
            "Element": "Skirting",
            "Description": f"Skirting to {room_name}",
            "Unit": "m",
            "Quantity": round(perimeter, 2)
        })

        # --- Openings (windows/doors) ---
        for o in openings:
            if o["width_m"] and o["height_m"]:
                opening_area = round(o["width_m"] * o["height_m"], 2)
                boq_entries.append({
                    "Room": room_name,
                    "Element": "Windows" if o["tag"].startswith("W") else "Doors",
                    "Description": f"{o['tag']} in {room_name} ({o['count']} no.)",
                    "Unit": "No.",
                    "Quantity": o["count"]
                })

    return boq_entries

# Example usage
if __name__ == "__main__":
    entries = parse_floorplan("sample_floorplan.pdf")
    for e in entries:
        print(e)



