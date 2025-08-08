import pdfplumber
import re
from math import sqrt

def distance(a, b):
    return sqrt((a["x"] - b["x"])**2 + (a["y"] - b["y"])**2)

def extract_pdf_text(pdf_path):
    room_names = []
    dimensions = []

    room_keywords = [
        "living", "bedroom", "kitchen", "bath", "store", "dining", "foyer", "passage", "master", "madam", "children", "ent"
    ]

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            words = page.extract_words()
            for word in words:
                text = word['text'].strip().lower()
                pos = {"x": word['x0'], "y": word['top'], "page": i + 1}

                if any(k in text for k in room_keywords):
                    room_names.append({**pos, "room": text})

                if re.fullmatch(r"\d{3,5}", text):
                    val = int(text)
                    if 500 <= val <= 30000:
                        dimensions.append({**pos, "value": val})

    # Associate dimensions to rooms
    associated = []
    for room in room_names:
        same_page_dims = [d for d in dimensions if d["page"] == room["page"]]
        dists = sorted(same_page_dims, key=lambda d: distance(room, d))
        unique_dims = []
        seen = set()
        for d in dists:
            if d["value"] not in seen:
                unique_dims.append(d["value"])
                seen.add(d["value"])
            if len(unique_dims) == 2:
                break

        if len(unique_dims) == 2:
            length, width = sorted(unique_dims, reverse=True)
            area = round((length * width) / 1_000_000, 2)  # m²
        else:
            length, width, area = None, None, None

        associated.append({
            "room": room["room"].title(),
            "page": room["page"],
            "length_mm": length,
            "width_mm": width,
            "area_m2": area
        })

    return associated


