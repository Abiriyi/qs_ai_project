# pdf_parser.py
import pdfplumber
import re
from math import hypot


def extract_pdf_text(pdf_path):
    rooms_data = []
    heights_data = []
    openings = []
    other_elements = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words() or []
            page_text = page.extract_text() or ""

            # --- Room detection ---
            current_room = None
            for w in words:
                text = w["text"].strip()
                x, y = w["x0"], w["top"]

                # Room detection (avoid tags like W1/D2)
                if re.match(r"^[A-Za-z]", text) and not re.match(r"^[WD]\d", text, re.I):
                    current_room = text
                    rooms_data.append({
                        "Room": text,
                        "x": x,
                        "y": y,
                        "Page": page_num
                    })

                # Height detection
                if text.isdigit():
                    val = int(text)
                    if 2000 <= val <= 5000:
                        heights_data.append({"Height": val / 1000.0, "Page": page_num, "y": y})

                # Opening tags
                m = re.match(r"^([WD]\d+)$", text, re.I)
                if m:
                    tag = m.group(1).upper()
                    openings.append({
                        "tag": tag,
                        "count": 1,
                        "width_m": None,
                        "height_m": None,
                        "x": x,
                        "y": y,
                        "page": page_num
                    })

            # --- Dimension extraction for rooms ---
            lines = page_text.split("\n")
            for line in lines:
                dims = re.findall(r"\b\d{3,5}\b", line)
                dims_in_m = [int(n) / 1000.0 for n in dims if int(n) > 500]
                if current_room and len(dims_in_m) >= 2:
                    length, width = dims_in_m[:2]
                    area = round(length * width, 2)
                    perimeter = round(2 * (length + width), 2)
                    for r in rooms_data:
                        if r["Room"] == current_room and "Area" not in r:
                            r.update({
                                "Length": length,
                                "Width": width,
                                "Area": area,
                                "Perimeter": perimeter
                            })

            # --- Heuristic detections for other work sections ---
            if re.search(r"excavation|foundation", page_text, re.I):
                other_elements.append({"Element": "Substructure Works", "Description": "Excavation/Foundation", "Unit": "m³", "Quantity": None})
            if re.search(r"column|slab|beam", page_text, re.I):
                other_elements.append({"Element": "Superstructure Works", "Description": "Concrete structural works", "Unit": "m³", "Quantity": None})
            if re.search(r"tile|plaster|paint", page_text, re.I):
                other_elements.append({"Element": "Finishes", "Description": "Wall/Floor/Ceiling finishes", "Unit": "m²", "Quantity": None})
            if re.search(r"door|window", page_text, re.I):
                other_elements.append({"Element": "Fittings & Fixtures", "Description": "Doors/Windows fittings", "Unit": "No.", "Quantity": None})
            if re.search(r"electrical|light|switch|socket", page_text, re.I):
                other_elements.append({"Element": "Mechanical & Electrical Works", "Description": "Electrical installations", "Unit": "Item", "Quantity": None})
            if re.search(r"plumbing|pipe|water closet", page_text, re.I):
                other_elements.append({"Element": "Mechanical & Electrical Works", "Description": "Plumbing works", "Unit": "Item", "Quantity": None})
            if re.search(r"paving|fence|gate|landscape", page_text, re.I):
                other_elements.append({"Element": "External Works", "Description": "External site works", "Unit": "m²", "Quantity": None})

    # Assign nearest height per room
    for room in rooms_data:
        nearest_height = None
        min_dist = float("inf")
        for h in heights_data:
            dist = abs(room["y"] - h["y"]) if "y" in h else 9999
            if dist < min_dist:
                nearest_height = h["Height"]
                min_dist = dist
        room["Height"] = nearest_height if nearest_height else 3.0

    return {"rooms": rooms_data, "heights": heights_data, "openings": openings, "others": other_elements}







