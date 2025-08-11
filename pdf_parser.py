import pdfplumber
import re

def extract_pdf_text(pdf_path):
    """
    Extracts either:
      - Room name + L×W from floor plan PDFs
      - Wall heights from section PDFs
    """
    rooms_data = []
    heights_data = []

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



