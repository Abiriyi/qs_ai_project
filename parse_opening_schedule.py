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
    Parse a doors & windows schedule PDF and return openings library.

    Returns:
      openings_lib = {
        "W1": {"type": "window", "count": 4, "width_m": 1.2, "height_m": 1.5},
        "D2": {"type": "door", "count": 2, "width_m": 0.9, "height_m": 2.1},
        ...
      }
    Notes:
      - If sizes are not found, width_m/height_m may be None (we'll provide defaults later).
      - The parser uses heuristics to handle many schedule styles.
    """
    # results collected per tag
    openings = defaultdict(lambda: {"type": None, "count": 0, "width_m": None, "height_m": None, "raw": []})

    with pdfplumber.open(pdf_path) as pdf:
        # flatten all text for easier pattern search; but also keep token positions if needed
        full_text = ""
        pages_text = []
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)
            full_text += "\n" + page_text

    # common patterns:
    # Tag: W1 or w1 or D2
    tag_pattern = re.compile(r"\b([WD]\d{1,3})\b", re.IGNORECASE)

    # size pattern: 1200x1500 or 1200 x 1500
    size_x_pattern = re.compile(r"(\d{3,5})\s*[xX]\s*(\d{3,5})")

    # two numbers following a tag: W1 1200 1500
    two_numbers_pattern = re.compile(r"\b([WD]\d{1,3})\b[^\S\r\n]{0,6}?(\d{3,5})[^\S\r\n]{1,6}(\d{3,5})")

    # counts like "W1 - 4 nos" or "W1 4 NO"
    count_pattern = re.compile(r"\b([WD]\d{1,3})\b[^\S\r\n]{0,8}?(\d{1,4})\s*(?:no|nos|nos\.|no\.)\b", re.IGNORECASE)

    # Try to find explicit "Tag width x height" patterns across whole page
    for m in size_x_pattern.finditer(full_text):
        # look backwards a short window to see if a tag appears nearby
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

    # Try two-number patterns (W1 1200 1500)
    for m in two_numbers_pattern.finditer(full_text):
        tag = m.group(1).upper()
        w_mm, h_mm = m.group(2), m.group(3)
        # Only set if not already set by previous pattern
        if openings[tag]["width_m"] is None:
            openings[tag]["width_m"] = _to_m(w_mm)
        if openings[tag]["height_m"] is None:
            openings[tag]["height_m"] = _to_m(h_mm)
        openings[tag]["raw"].append(("two_numbers", f"{w_mm} {h_mm}"))
        if verbose:
            print(f"Found two numbers for {tag}: {w_mm} {h_mm}")

    # Try explicit count patterns
    for m in count_pattern.finditer(full_text):
        tag = m.group(1).upper()
        count = int(m.group(2))
        openings[tag]["count"] = max(openings[tag]["count"], count)
        openings[tag]["raw"].append(("count_text", str(count)))
        if verbose:
            print(f"Found count for {tag}: {count}")

    # If no counts found near tags, try to parse explicit count table lines like: "W1 04" or "W1 4"
    simple_tag_count = re.compile(r"\b([WD]\d{1,3})\b[^\S\r\n]{1,6}?0?([1-9]\d?)\b")
    for m in simple_tag_count.finditer(full_text):
        tag = m.group(1).upper()
        count = int(m.group(2))
        openings[tag]["count"] = max(openings[tag]["count"], count)
        openings[tag]["raw"].append(("simple_count", str(count)))
        if verbose:
            print(f"Found simple count for {tag}: {count}")

    # If we still have tags with no counts, try to find "Total Quantity" lines near tag names
    # --- fallback: set count to 1 if nothing else found
    for tag in list(openings.keys()):
        if openings[tag]["count"] == 0:
            openings[tag]["count"] = 1

    # Determine type heuristically: tag starts with W => window, D => door
    openings_lib = {}
    for tag, info in openings.items():
        typ = "window" if tag.upper().startswith("W") else "door" if tag.upper().startswith("D") else "other"
        openings_lib[tag] = {
            "type": typ,
            "count": info["count"],
            "width_m": info["width_m"],
            "height_m": info["height_m"],
            "raw": info["raw"]
        }

    return openings_lib
