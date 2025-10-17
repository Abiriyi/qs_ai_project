# parse_section.py
import re
import pdfplumber

DEFAULT_CEILING_HEIGHT_M = 3.3
DEFAULT_FDTN_DEPTH_M = 1.0
DEFAULT_SLAB_THICKNESS_M = 0.15

def parse_section(pdf_path, verbose=False):
    """
    Parse building section PDF for heights, slabs, foundations.
    Returns BoQ entries for Substructure + Superstructure.
    """
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])

    boq_entries = []

    # --- Floor-to-floor heights ---
    height_matches = re.findall(r"(\d+\.\d+)\s*m", full_text)
    if height_matches:
        ceiling_height = max(map(float, height_matches))
    else:
        ceiling_height = DEFAULT_CEILING_HEIGHT_M
    if verbose:
        print(f"Detected ceiling height: {ceiling_height}m")

    boq_entries.append({
        "Room": "ALL",
        "Element": "Ceiling Finish",
        "Description": f"Ceiling at approx {ceiling_height}m",
        "Unit": "m²",
        "Quantity": 0,  # filled later via floorplan areas
        "WorkSection": "Finishes"
    })

    # --- Foundation depth ---
    fdn_depth = DEFAULT_FDTN_DEPTH_M
    if "foundation" in full_text.lower():
        m = re.search(r"(\d+\.\d+)\s*m\s*deep", full_text.lower())
        if m:
            fdn_depth = float(m.group(1))
    boq_entries.append({
        "Room": "ALL",
        "Element": "Foundations",
        "Description": f"Foundations approx {fdn_depth}m deep",
        "Unit": "m³",
        "Quantity": 0,  # needs area from site/floor
        "WorkSection": "Substructure Works"
    })

    # --- Slab thickness ---
    slab_thickness = DEFAULT_SLAB_THICKNESS_M
    m = re.search(r"(\d+)\s*mm\s*slab", full_text.lower())
    if m:
        slab_thickness = int(m.group(1)) / 1000
    boq_entries.append({
        "Room": "ALL",
        "Element": "Ground Floor Slab",
        "Description": f"Reinforced concrete slab {slab_thickness:.2f}m thick",
        "Unit": "m²",
        "Quantity": 0,
        "WorkSection": "Substructure Works"
    })

    return boq_entries

