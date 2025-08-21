from math import hypot

EXCLUDE_TERMS = ["residential", "development"]

def build_boq_entries(parsed_data):
    rooms_tokens = parsed_data.get("rooms", [])
    heights = parsed_data.get("heights", [])
    openings = parsed_data.get("openings", [])

    # --- build room objects with area/perimeter
    rooms = []
    for r in rooms_tokens:
        rooms.append({
            "Room": r["Room"],
            "x": r.get("x", 0),
            "y": r.get("y", 0),
            "Area": r.get("Area", 0),
            "Perimeter": r.get("Perimeter", 0),
            "Page": r.get("Page", 1)
        })

    # --- determine average height if available
    avg_height = 3.0
    if heights:
        avg_height = round(sum(h["Height"] for h in heights) / len(heights), 2)

    # --- assign openings to nearest room (if positions exist)
    for op in openings:
        same_page_rooms = [rm for rm in rooms if rm.get("Page", 1) == op.get("page", 1)]
        if same_page_rooms:
            nearest = min(same_page_rooms, key=lambda r: hypot(r["x"] - op.get("x", 0), r["y"] - op.get("y", 0)))
        else:
            nearest = rooms[0] if rooms else None
        if nearest:
            op["room"] = nearest["Room"]

    # --- aggregate opening areas per room
    openings_by_room = {}
    for op in openings:
        room = op.get("room")
        if not room:
            continue
        w = op.get("width_m")
        h = op.get("height_m")
        count = op.get("count", 1)
        if w and h:
            area = w * h * count
        else:
            # defaults if size not known
            if op["tag"].startswith("W"):
                area = 1.2 * 1.5 * count
            else:
                area = 0.9 * 2.1 * count
        openings_by_room[room] = openings_by_room.get(room, 0) + area

    # --- build BoQ entries
    boq_entries = []
    for rm in rooms:
        room_name = rm["Room"]
        if any(term in room_name.lower() for term in EXCLUDE_TERMS):
            continue

        area = rm.get("Area", 0)
        perimeter = rm.get("Perimeter", 0)
        opening_area = openings_by_room.get(room_name, 0)

        # Floor finish
        if area > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Floor Finish",
                "Description": f"Floor tiling to {room_name}",
                "Quantity": round(area, 2),
                "Unit": "m²"
            })

        # Wall finish (deduct openings)
        wall_area = round(max(perimeter * avg_height - opening_area, 0), 2)
        if wall_area > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Wall Finish",
                "Description": f"Plastering to walls in {room_name}",
                "Quantity": wall_area,
                "Unit": "m²"
            })

        # Skirting
        if perimeter > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Skirting",
                "Description": f"Skirting to {room_name}",
                "Quantity": round(perimeter, 2),
                "Unit": "m"
            })

        # Ceiling finish
        if area > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Ceiling Finish",
                "Description": f"Ceiling finish to {room_name}",
                "Quantity": round(area, 2),
                "Unit": "m²"
            })

    return boq_entries


