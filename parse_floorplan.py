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
