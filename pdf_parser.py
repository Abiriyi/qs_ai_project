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
            numeric_buffer = []

            for w in words:
                text = w["text"].strip()
                x, y = w["x0"], w["top"]

                # Room detection (avoid W1, D2)
                if re.match(r"^[A-Za-z]", text) and not re.match(r"^[WD]\d", text, re.I):
                    current_room = text
                    numeric_buffer = []
                    rooms_data.append({
                        "Room": text,
                        "x": x,
                        "y": y,
                        "Page": page_num
                    })

                # Height detection from numeric tokens
                if text.isdigit():
                    val = int(text)
                    if 2000 <= val <= 5000:
                        heights_data.append({"Height": val / 1000.0, "Page": page_num})

                # Opening tag detection
                m = re.match(r"^([WD]\d+)$", text, re.I)
                if m:
                    tag = m.group(1).upper()
                    width_m, height_m, count = None, None, 1

                    size_pattern = re.search(rf"{tag}[^A-Za-z0-9\-]*(\d{{3,5}})\s*[xX]\s*(\d{{3,5}})", page_text)
                    if size_pattern:
                        width_m = int(size_pattern.group(1)) / 1000.0
                        height_m = int(size_pattern.group(2)) / 1000.0
                    else:
                        size_pattern2 = re.search(rf"{tag}[^A-Za-z0-9\-]*(\d{{3,5}})\s+(\d{{3,5}})", page_text)
                        if size_pattern2:
                            width_m = int(size_pattern2.group(1)) / 1000.0
                            height_m = int(size_pattern2.group(2)) / 1000.0
                        else:
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

            # --- Dimension extraction for current room (from full text) ---
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
                            r.update({"Length": length, "Width": width, "Area": area, "Perimeter": perimeter})

    return {"rooms": rooms_data, "heights": heights_data, "openings": openings}



