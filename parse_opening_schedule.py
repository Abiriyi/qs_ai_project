# parse_opening_schedule.py
import re
from collections import defaultdict
import pdfplumber

def _to_m(val_str):
    """Convert a numeric string (mm) to meters as float. Handles commas."""
    v = int(val_str.replace(",", "").strip())
    return v / 1000.0

def parse_opening_schedule(pdf_path, verbose=False):
    """
    Parse a doors & windows schedule PDF and return openings library + BoQ entries.
    Returns:
      openings_lib (dict)
      boq_entries (list of dicts)
    """
    openings = defaultdict(lambda: {"type": None, "count": 0, "width_m": None, "height_m": None, "raw": []})

    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

    tag_pattern = re.compile(r"\b([WD]\d{1,3})\b", re.IGNORECASE)
    size_x_pattern = re.compile(r"(\d{3,5})\s*[xX]\s*(\d{3,5})")
    two_numbers_pattern = re.compile(r"\b([WD]\d{1,3})\b\s*(\d{3,5})\s+(\d{3,5})")
    count_pattern = re.compile(r"\b([WD]\d{1,3})\b\s*(\d{1,4})\s*(?:no|nos|no\.|nos\.)", re.IGNORECASE)
    simple_tag_count = re.compile(r"\b([WD]\d{1,3})\b\s*0?([1-9]\d?)\b")

    # Size patterns
    for m in size_x_pattern.finditer(full_text):
        start = max(0, m.start() - 40)
        context = full_text[start:m.start()]
        tag_match = tag_pattern.search(context)
        if tag_match:
            tag = tag_match.group(1).upper()
            w_mm, h_mm = m.group(1), m.group(2)
            openings[tag]["width_m"] = _to_m(w_mm)
            openings[tag]["height_m"] = _to_m(h_mm)
            openings[tag]["raw"].append(("size_x", m.group(0)))
            if verbose:
                print(f"Found size {m.group(0)} for tag {tag}")

    # Two-number patterns
    for m in two_numbers_pattern.finditer(full_text):
        tag = m.group(1).upper()
        w_mm, h_mm = m.group(2), m.group(3)
        if openings[tag]["width_m"] is None:
            openings[tag]["width_m"] = _to_m(w_mm)
        if openings[tag]["height_m"] is None:
            openings[tag]["height_m"] = _to_m(h_mm)
        openings[tag]["raw"].append(("two_numbers", f"{w_mm} {h_mm}"))

    # Count patterns
    for m in count_pattern.finditer(full_text):
        tag = m.group(1).upper()
        openings[tag]["count"] = max(openings[tag]["count"], int(m.group(2)))
        openings[tag]["raw"].append(("count_text", m.group(2)))

    for m in simple_tag_count.finditer(full_text):
        tag = m.group(1).upper()
        openings[tag]["count"] = max(openings[tag]["count"], int(m.group(2)))
        openings[tag]["raw"].append(("simple_count", m.group(2)))

    # Defaults
    for tag in list(openings.keys()):
        if openings[tag]["count"] == 0:
            openings[tag]["count"] = 1

    # Normalize + build BoQ entries
    openings_lib, boq_entries = {}, []
    for tag, info in openings.items():
        typ = "window" if tag.startswith("W") else "door" if tag.startswith("D") else "other"
        openings_lib[tag] = {
            "type": typ,
            "count": info["count"],
            "width_m": info["width_m"],
            "height_m": info["height_m"],
            "raw": info["raw"],
        }

        boq_entries.append({
            "Room": "ALL",
            "Element": "Windows" if typ == "window" else "Doors",
            "Description": f"{tag} ({info['count']} no.)",
            "Unit": "No.",
            "Quantity": info["count"],
            "WorkSection": "Superstructure Works"
        })

    return openings_lib, boq_entries

