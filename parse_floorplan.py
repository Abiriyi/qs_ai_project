def build_boq_entries(parsed_data):
    """
    Builds BoQ entries for:
      - Floor finishes
      - Skirting
      - Wall plastering (if heights detected)
    """
    boq_entries = []

    rooms_data = parsed_data.get("rooms", [])
    heights_data = parsed_data.get("heights", [])

    # Default wall height if no section data
    default_height = 3.0
    avg_height = default_height

    if heights_data:
        avg_height = round(sum(h["Height"] for h in heights_data) / len(heights_data), 2)
        print(f"📏 Average wall height from sections: {avg_height} m")

    for room in rooms_data:
        # Floor finish
        boq_entries.append({
            "Room": room["Room"],
            "Element": "Floor Finish",
            "Description": f"Floor tiling to {room['Room']}",
            "Quantity": room["Area"],
            "Unit": "m²"
        })

        # Skirting (perimeter)
        boq_entries.append({
            "Room": room["Room"],
            "Element": "Skirting",
            "Description": f"Skirting to {room['Room']}",
            "Quantity": room["Perimeter"],
            "Unit": "m"
        })

        # Wall finish (plastering area)
        wall_area = round(room["Perimeter"] * avg_height, 2)
        boq_entries.append({
            "Room": room["Room"],
            "Element": "Wall Finish",
            "Description": f"Plastering to walls in {room['Room']}",
            "Quantity": wall_area,
            "Unit": "m²"
        })

    return boq_entries
def build_boq_entries(rooms):
    """
    Converts raw room measurements into structured BoQ entries.
    rooms: list of dicts with keys Room, Area, Perimeter
    """
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

        # Wall finish (paint)
        boq_entries.append({
            "Room": room_name,
            "Element": "Wall Finish",
            "Description": f"Emulsion paint on walls in {room_name}",
            "Quantity": round(perimeter * 2.8, 2),  # 2.8m assumed wall height
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
