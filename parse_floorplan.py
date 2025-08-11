def build_boq_entries(parsed_data):
    rooms_tokens = parsed_data.get("rooms", [])
    heights = parsed_data.get("heights", [])
    openings = parsed_data.get("openings", [])

    # --- build room centroids: if tokens include multiple tokens per room, you may want to aggregate.
    # For simplicity assume rooms_tokens are single labels with x,y
    rooms = []
    for r in rooms_tokens:
        # try to get L,W,Area,Perimeter via earlier floorplan extractor if available
        # fallback: set Area/Perimeter = 0 (we will rely on floorplan parser to supply these normally)
        rooms.append({
            "Room": r["Room"],
            "x": r["x"],
            "y": r["y"],
            "Area": r.get("Area", 0),
            "Perimeter": r.get("Perimeter", 0)
        })

    # compute average height from section heights if present
    avg_height = 3.0
    if heights:
        avg_height = round(sum(h["Height"] for h in heights) / len(heights), 2)

    # Map openings to nearest room token by Euclidean distance (only on same page)
    for op in openings:
        # find nearest room on same page
        same_page_rooms = [rm for rm in rooms if rm.get("Page", 1) == op.get("page", 1)]
        if not same_page_rooms:
            same_page_rooms = rooms
        nearest = min(same_page_rooms, key=lambda r: hypot(r["x"] - op["x"], r["y"] - op["y"]))
        op["room"] = nearest["Room"]

    # Aggregate opening areas per room
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
            # if only count known (no size), assume typical sizes (optional)
            # example defaults:
            if op["tag"].startswith("W"):
                area = 1.2 * 1.5 * count  # default window 1200x1500
            else:
                area = 0.9 * 2.1 * count  # default door 900x2100
        openings_by_room[room] = openings_by_room.get(room, 0) + area

    # Build BoQ entries using floor area/perimeter, subtract opening area from wall area
    boq_entries = []
    for rm in rooms:
        room_name = rm["Room"]
        area = rm.get("Area", 0)
        perimeter = rm.get("Perimeter", 0)
        opening_area = openings_by_room.get(room_name, 0)

        # floor finish
        if area > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Floor Finish",
                "Description": f"Floor tiling to {room_name}",
                "Quantity": round(area, 2),
                "Unit": "m²"
            })

        # wall area = perimeter * height - openings
        wall_area = round(max(perimeter * avg_height - opening_area, 0), 2)
        if wall_area > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Wall Finish",
                "Description": f"Plastering to walls in {room_name}",
                "Quantity": wall_area,
                "Unit": "m²"
            })

        # skirting
        if perimeter > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Skirting",
                "Description": f"Skirting to {room_name}",
                "Quantity": round(perimeter, 2),
                "Unit": "m"
            })

        # ceiling
        if area > 0:
            boq_entries.append({
                "Room": room_name,
                "Element": "Ceiling Finish",
                "Description": f"Ceiling finish to {room_name}",
                "Quantity": round(area, 2),
                "Unit": "m²"
            })

    return boq_entries

