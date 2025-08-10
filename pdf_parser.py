import pdfplumber
import re
from math import sqrt

def extract_pdf_text(pdf_path):
    """
    Extract rooms with calculated area & perimeter from a floor plan PDF.
    Returns: list of dicts with Room, Area (m²), Perimeter (m)
    """
    rooms_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = text.split("\n")

            current_room = None
            length = None
            width = None

            for line in lines:
                # Try to detect room name (very simple rule: words with letters)
                if re.match(r"^[A-Za-z].*", line):
                    current_room = line.strip()

                # Detect a dimension (e.g., '4500 mm' or '4.5 m')
                dim_match = re.findall(r"(\d+(?:\.\d+)?)\s*(mm|m)\b", line)
                if dim_match:
                    # Convert to meters
                    dims_in_m = []
                    for value, unit in dim_match:
                        val = float(value)
                        if unit == "mm":
                            val /= 1000.0
                        dims_in_m.append(val)

                    if len(dims_in_m) == 2:
                        length, width = dims_in_m
                        area = round(length * width, 2)
                        perimeter = round(2 * (length + width), 2)

                        if current_room:
                            rooms_data.append({
                                "Room": current_room,
                                "Area": area,
                                "Perimeter": perimeter
                            })
                            current_room = None
                            length = None
                            width = None

    return rooms_data


