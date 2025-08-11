# pdf_parser.py additions (or replace the file with merged content)
import pdfplumber
import re
from math import hypot

def _distance(a, b):
    return hypot(a["x"] - b["x"], a["y"] - b["y"])

def extract_pdf_text(pdf_path):
    """
    Returns:
      {
        "rooms": [ {Room, Length, Width, Area, Perimeter, x, y, Page}, ... ],
        "heights": [ {"Height": m, "Page": n}, ... ],
        "openings": [ {"tag":"W1","count":n,"width_m":w,"height_m":h,"x":x,"y":y,"page":p}, ... ]
      }
    """
    rooms_data = []
    heights_data = []
    openings = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words()  # gives positions
            # Build quick map of text tokens with positions
            for w in words:
                text = w["text"].strip()
                x = w["x0"]
                y = w["top"]

                # Detect room name (approx)
                if re.match(r"^[A-Za-z].*", text) and not re.match(r"^[WD]\d", text, re.I):
                    # store room tokens: we'll aggregate later in simpler parser
                    rooms_data.append({"Room": text, "x": x, "y": y, "Page": page_num})

                # Detect numeric tokens that are likely dimensions (3-5 digits)
                # handled elsewhere or by existing logic (keep compatibility)

                # Detect opening tags like W1, D2, w3, d4
                m = re.match(r"^([WD]\d+)$", text, re.I)
                if m:
                    tag = m.group(1).upper()
                    # Try to find size right after tag on same page (e.g., 1200x1500 or 1200 1500)
                    # Look in nearby words
                    width_m = None
                    height_m = None
                    count = 1
                    # scan next few words
                    for neighbor in words:
                        # only consider same page by design
                        pass
                    # Simple heuristic: search text stream for patterns like 1200x1500 or 1200 X 1500
                    # fallback: search whole page text for occurrences like "W1 1200x1500" or "W1 - 1200 x 1500"
                    page_text = page.extract_text() or ""
                    # regex for W1 1200x1500 or W1 1200 x 1500
                    size_pattern = re.search(rf"{tag}[^A-Za-z0-9\-]*(\d{{3,5}})\s*[xX]\s*(\d{{3,5}})", page_text)
                    if size_pattern:
                        w_px = int(size_pattern.group(1))
                        h_px = int(size_pattern.group(2))
                        width_m = w_px / 1000.0
                        height_m = h_px / 1000.0
                    else:
                        # try "W1 1200 1500" pattern
                        size_pattern2 = re.search(rf"{tag}[^A-Za-z0-9\-]*(\d{{3,5}})\s+(\d{{3,5}})", page_text)
                        if size_pattern2:
                            w_px = int(size_pattern2.group(1))
                            h_px = int(size_pattern2.group(2))
                            width_m = w_px / 1000.0
                            height_m = h_px / 1000.0
                        else:
                            # try to find counts like "W1 - 4nos" or "W1 4 NO"
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

                # Detect heights (2–5m) from section views
                hmatch = re.findall(r"\b\d{3,4}\b", text)
                for h in hmatch:
                    hv = int(h)
                    if 2000 <= hv <= 5000:
                        heights_data.append({"Height": hv / 1000.0, "Page": page_num})

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = text.split("\n")

            current_room = None
            numeric_buffer = []

            for line in lines:
                # Look for wall heights (e.g., "3000", "3150") between 2.0m–5.0m
                height_matches = re.findall(r"\b\d{3,4}\b", line)
                for h in height_matches:
                    h_val = int(h)
                    if 2000 <= h_val <= 5000:  # between 2m and 5m
                        heights_data.append({
                            "Height": h_val / 1000.0,  # convert mm to m
                            "Page": page_num
                        })

                # Room name detection (letters only, ignoring W2, D4 etc.)
                if re.match(r"^[A-Za-z]", line) and not re.match(r"^[WD]\d", line):
                    current_room = line.strip()
                    numeric_buffer = []

                # Extract numeric dimensions (3–5 digits)
                numbers = re.findall(r"\b\d{3,5}\b", line)
                dims_in_m = [int(n) / 1000.0 for n in numbers if int(n) > 500]
                numeric_buffer.extend(dims_in_m)

                # If we have a room and two dimensions, store L×W
                if current_room and len(numeric_buffer) >= 2:
                    length, width = numeric_buffer[0], numeric_buffer[1]
                    area = round(length * width, 2)
                    perimeter = round(2 * (length + width), 2)

                    rooms_data.append({
                        "Room": current_room,
                        "Length": length,
                        "Width": width,
                        "Area": area,
                        "Perimeter": perimeter,
                        "Page": page_num
                    })

                    current_room = None
                    numeric_buffer = []

    return {"rooms": rooms_data, "heights": heights_data}



