# parse_floorplan.py
from pdf_parser import extract_pdf_text


def build_boq_entries(parsed_data, location=None):
    """
    Build BoQ entries from parsed PDF data covering all work sections.
    """
    rooms = parsed_data.get("rooms", [])
    openings = parsed_data.get("openings", [])
    others = parsed_data.get("others", [])

    boq_entries = []

    # Finishes, Fittings, and room-based work
    for room in rooms:
        room_name = room.get("Room", "Unknown")
        area = room.get("Area", 0)
        perimeter = room.get("Perimeter", 0)
        height = room.get("Height", 3.0)

        if area and perimeter:
            boq_entries.append({"Room": room_name, "Element": "Floor Finish", "Description": f"Floor tiling to {room_name}", "Unit": "m²", "Quantity": round(area, 2)})
            boq_entries.append({"Room": room_name, "Element": "Wall Finish", "Description": f"Wall plastering/painting in {room_name}", "Unit": "m²", "Quantity": round(perimeter * height, 2)})
            boq_entries.append({"Room": room_name, "Element": "Ceiling Finish", "Description": f"Ceiling finish to {room_name}", "Unit": "m²", "Quantity": round(area, 2)})
            boq_entries.append({"Room": room_name, "Element": "Skirting", "Description": f"Skirting to {room_name}", "Unit": "m", "Quantity": round(perimeter, 2)})

        for o in openings:
            boq_entries.append({"Room": room_name, "Element": "Windows" if o["tag"].startswith("W") else "Doors", "Description": f"{o['tag']} in {room_name} ({o['count']} no.)", "Unit": "No.", "Quantity": o["count"]})

    # Add heuristic detections
    boq_entries.extend(others)

    # Add preliminaries and provisional sums as placeholders
    boq_entries.append({"Room": None, "Element": "Preliminaries", "Description": "Site establishment, preliminaries", "Unit": "Item", "Quantity": 1})
    boq_entries.append({"Room": None, "Element": "Provisional & Prime Cost Sums", "Description": "Provisional sum (allowance)", "Unit": "Item", "Quantity": 1})

    return boq_entries



