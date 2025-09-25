# pdf_parse.py
import pdfplumber
import re
from math import hypot

def extract_pdf_text(pdf_path):
    rooms_data = []
    heights_data = []
    openings = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words()
            page_text = page.extract_text() or ""

            # --- Room names & coordinates ---
            current_room = None

            for w in words:
                text = w["text"].strip()
                x, y = w["x0"], w["top"]

                # Detect room names (skip opening tags W1, D2, etc.)
                if re.match(r"^[A-Za-z]", text) and not re.match(r"^[WD]\d", text, re.I):
                    current_room = {
                        "Room": text,
                        "x": x,
                        "y": y,
                        "Page": page_num,
                        "Area": None,
                        "Perimeter": None,
                        "Height": None
                    }
                    rooms_data.append(current_room)

                # Detect ceiling/wall heights (2000–5000 mm)
                if text.isdigit():
                    val = int(text)
                    if 2000 <= val <= 5000:
                        height_m = val / 1000.0
                        heights_data.append({"Height": height_m, "Page": page_num})

                        # assign nearest room this height
                        if rooms_data:
                            nearest = min(
                                rooms_data,
                                key=lambda r: abs(r["y"] - y) + abs(r["x"] - x)
                            )
                            nearest["Height"] = height_m

                # Detect openings (doors/windows)
                m = re.match(r"^([WD]\d+)$", text, re.I)
                if m:
                    tag = m.group(1).upper()
                    width_m, height_m, count = None, None, 1

                    # Pattern 1200x1500
                    size_pattern = re.search(rf"{tag}[^A-Za-z0-9\-]*(\d{{3,5}})\s*[xX]\s*(\d{{3,5}})", page_text)
                    if size_pattern:
                        width_m = int(size_pattern.group(1)) / 1000.0
                        height_m = int(size_pattern.group(2)) / 1000.0

                    # Pattern 1200 1500
                    else:
                        size_pattern2 = re.search(rf"{tag}[^A-Za-z0-9\-]*(\d{{3,5}})\s+(\d{{3,5}})", page_text)
                        if size_pattern2:
                            width_m = int(size_pattern2.group(1)) / 1000.0
                            height_m = int(size_pattern2.group(2)) / 1000.0

                    # Count like W1 4 nos
                    count_pattern = re.search(rf"{tag}[^A-Za-z0-9\-]*(\d{{1,3}})\s*(?:no|nos|nos\.)", page_text, re.I)
                    if count_pattern:
                        count = int(count_pattern.group(1))

                    openings.append({
                        "tag": tag,
                        "count": count,
                        "width_m": width_m,
                        "height_m": height_m,
                        "x": x,
                        "y": y,
                        "page": page_num
                    })

            # --- Room dimensions from text lines ---
            lines = page_text.split("\n")
            for line in lines:
                # detect patterns like "3600x4200"
                size_pattern = re.search(r"(\d{3,5})\s*[xX]\s*(\d{3,5})", line)
                if size_pattern and current_room:
                    length = int(size_pattern.group(1)) / 1000.0
                    width = int(size_pattern.group(2)) / 1000.0
                    area = round(length * width, 2)
                    perimeter = round(2 * (length + width), 2)

                    current_room.update({
                        "Length": length,
                        "Width": width,
                        "Area": area,
                        "Perimeter": perimeter
                    })

    # Fallbacks: if a room has no height, assign average of detected heights
    if heights_data:
        avg_height = round(sum(h["Height"] for h in heights_data) / len(heights_data), 2)
        for r in rooms_data:
            if not r.get("Height"):
                r["Height"] = avg_height
    else:
        for r in rooms_data:
            r["Height"] = 3.0  # last fallback

    return {"rooms": rooms_data, "heights": heights_data, "openings": openings}




