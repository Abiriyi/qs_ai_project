# parse_opening_schedule.py
import re
from collections import defaultdict
import pdfplumber


def _to_m(val_str):
    """Convert a numeric string (mm) to meters as float. Handles commas, decimals, etc."""
    val_str = val_str.strip().replace(",", "")
    try:
        v = float(val_str)
        # Assume mm if > 20 (since windows rarely 20 m wide)
        return v / 1000.0 if v > 20 else v
    except Exception:
        return None


def parse_opening_schedule(pdf_path, verbose=False):
    """
    Parse a doors & windows schedule PDF and return:
      openings_lib (dict)
      boq_entries (list of dicts)
    Each BoQ entry follows the structure required by the BESMM4 pipeline.
    """
    openings = defaultdict(lambda: {"type": None, "count": 0, "width_m": None, "height_m": None, "raw": []})

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
    except Exception as e:
        print(f"⚠️ Could not open {pdf_path}: {e}")
        return {}, []

    # Common patterns
    tag_pattern = re.compile(r"\b([WD]\d{1,3})\b", re.IGNORECASE)
    size_x_pattern = re.compile(r"(\d{3,5})\s*[xX×]\s*(\d{3,5})")
    count_pattern = re.compile(r"\b([WD]\d{1,3})\b\s*(\d{1,3})\s*(?:no|nos|no\.|nos\.)", re.IGNORECASE)
    simple_tag_count = re.compile(r"\b([WD]\d{1,3})\b\s*0?([1-9]\d?)\b")

    # Match size formats like "W01 1200x1500" or "D02 900 X 2100"
    for m in size_x_pattern.finditer(full_text):
        w_mm, h_mm = m.group(1), m.group(2)
        start = max(0, m.start() - 50)
        context = full_text[start:m.start()]
        tag_match = tag_pattern.search(context)
        if tag_match:
            tag = tag_match.group(1).upper()
            openings[tag]["width_m"] = _to_m(w_mm)
            openings[tag]["height_m"] = _to_m(h_mm)
            openings[tag]["raw"].append(("size", f"{w_mm}x{h_mm}"))
            if verbose:
                print(f"✅ Found size for {tag}: {w_mm}x{h_mm}")

    # Counts
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

    # Normalize + create BoQ entries
    openings_lib, boq_entries = {}, []
    for tag, info in openings.items():
        typ = "window" if tag.startswith("W") else "door" if tag.startswith("D") else "other"
        element = "Windows" if typ == "window" else "Doors"

        openings_lib[tag] = {
            "type": typ,
            "count": info["count"],
            "width_m": info["width_m"],
            "height_m": info["height_m"],
            "raw": info["raw"],
        }

        desc = f"{tag}: {typ.title()} {info['width_m'] or '?'}m × {info['height_m'] or '?'}m ({info['count']} No.)"

        boq_entries.append({
            "Room": "ALL",
            "Element": element,
            "Description": desc,
            "Unit": "No.",
            "Quantity": info["count"],
            "WorkSection": "Superstructure Works"
        })

    if verbose:
        print(f"✅ Extracted {len(boq_entries)} openings from {pdf_path}")

    return openings_lib, boq_entries


