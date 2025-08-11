from math import hypot

def build_boq_entries(parsed_data):
    rooms_tokens = parsed_data.get("rooms", [])
    heights = parsed_data.get("heights", [])
    openings = parsed_data.get("openings", [])

    rooms = []
    for r in rooms_tokens:
        rooms.append({
            "Room": r.get("Room", "Unknown Room"),
            "x": r.get("x", 0),
            "y": r.get("y", 0),
            "Page": r.get("Page", 1),
            "Area": r.get("Area", 0),
            "Perimeter": r.get("Perimeter", 0)
        })

    avg_height = 3.0
    if heights:
        avg_height = round(sum(h.get("Height", 3.0) for h in heights) / len(heights), 2)

    for op in openings:
        same_page_rooms = [rm for rm in rooms if rm.get("Page", 1) == op.get("page", 1)]
        if not same_page_rooms:
            same_page_rooms = rooms
        nearest = min(
            same_page_rooms,
            key=lambda r: hypot(r["x"] - op.get("x", 0), r["y"] - op.get("y", 0))
        )
        op["room"] = nearest["Room"]

    openings_by_room = {}
    for op in openings:
        room = op.get("room")
        if not room:
            continue
        w = op.get("width_m")
        h = op.get("height_m")
        count = op.get("count", 1)
        tag = op.get("tag", "")

        if w and h:
            area = w * h * count
        else:
            if tag.upper().startswith("W"):
                area = 1.2 * 1.5 * count
            else:
                area = 0.9 * 2.1 * count
        openings_by_room[room] = openings_by_room.get(room, 0) + area

    boq_entries = []
    for rm in rooms:
        room_name = rm["Room"]
        area = rm.get("Area", 0)
        perimeter = rm.get("Perimeter", 0)
        opening_area = openings_by_room.get(room_name, 0)

        if area > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Floor Finish",
                "Description": f"Floor tiling to {room_name}",
                "Quantity": round(area, 2),
                "Unit": "m²"
            })

        wall_area = round(max(perimeter * avg_height - opening_area, 0), 2)
        if wall_area > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Wall Finish",
                "Description": f"Plastering to walls in {room_name}",
                "Quantity": wall_area,
                "Unit": "m²"
            })

        if perimeter > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Skirting",
                "Description": f"Skirting to {room_name}",
                "Quantity": round(perimeter, 2),
                "Unit": "m"
            })

        if area > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Ceiling Finish",
                "Description": f"Ceiling finish to {room_name}",
                "Quantity": round(area, 2),
                "Unit": "m²"
            })

    return boq_entries

