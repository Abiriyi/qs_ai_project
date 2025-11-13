# main.py
import os
from dotenv import load_dotenv

from pdf_parser import extract_pdf_text
from parse_floorplan import build_boq_entries
from parse_section import parse_section as parse_section_pdf
from parse_opening_schedule import parse_opening_schedule
from boq_generator import generate_besmm4_boq

#from boq_generator import pluralize_worksection

load_dotenv()

def normalize_openings_lib(openings_lib):
    """Convert openings_lib dict -> list of opening dicts suitable for parsed_data['openings']"""
    openings_list = []
    for tag, data in (openings_lib or {}).items():
        openings_list.append({
            "tag": tag,
            "count": data.get("count", 1),
            "width_m": data.get("width_m"),
            "height_m": data.get("height_m"),
            "x": 0,
            "y": 0,
            "page": 1
        })
    return openings_list

if __name__ == "__main__":
    # Input drawings - edit as needed
    pdf_files = [
        "assets/floorplan.pdf",
        "assets/Section_X-X.pdf"
    ]
    openings_schedule_pdf = "assets/Doors and windows schedule.pdf"

    location = input("Enter project location for pricing (e.g., Abuja): ").strip() or "Kaduna"

    # 1) Parse openings schedule (if present)
    print(f"📄 Parsing openings schedule: {openings_schedule_pdf} ...")
    try:
        openings_result = parse_opening_schedule(openings_schedule_pdf, verbose=True)
    except Exception as e:
        print(f"⚠️ parse_opening_schedule failed: {e}")
        openings_result = {}

    # openings_result expected to be dict-like
    if isinstance(openings_result, tuple) and len(openings_result) >= 1:
        openings_lib = openings_result[0] or {}
    elif isinstance(openings_result, dict):
        openings_lib = openings_result
    else:
        openings_lib = {}

    openings_list_from_schedule = normalize_openings_lib(openings_lib)

    all_boq_entries = []

    # 2) For each input drawing, extract parsed data and create BoQ entries
    for pdf_path in pdf_files:
        print(f"📄 Processing drawing: {pdf_path} ...")
        if not os.path.exists(pdf_path):
            print(f"   ⚠️ File not found: {pdf_path} — skipping.")
            continue

        try:
            parsed = extract_pdf_text(pdf_path)
        except Exception as e:
            print(f"   ⚠️ extract_pdf_text failed for {pdf_path}: {e}")
            parsed = {"rooms": [], "heights": [], "openings": []}

        # merge schedule openings into parsed openings (avoid duplicates by tag)
        parsed.setdefault("openings", [])
        existing_tags = {op.get("tag") for op in parsed["openings"] if op.get("tag")}
        for op in openings_list_from_schedule:
            if op.get("tag") not in existing_tags:
                parsed["openings"].append(op)

        # Build room-based BoQ entries
        try:
            room_entries = build_boq_entries(parsed)
            if room_entries:
                all_boq_entries.extend(room_entries)
                print(f"   → Added {len(room_entries)} room-based entries.")
        except Exception as e:
            print(f"   ⚠️ build_boq_entries failed for {pdf_path}: {e}")

    # 3) Clean and normalize entries for generator
    cleaned_entries = []
    for e in all_boq_entries:
        qty = e.get("Quantity", e.get("Qty", 0)) or 0
        try:
            qty = float(qty)
        except Exception:
            try:
                qty = float(str(qty).replace(",", ""))
            except Exception:
                qty = 0.0

        cleaned_entries.append({
            "Room": str(e.get("Room") or ""),
            "Element": e.get("Element") or "Misc",
            "Description": e.get("Description") or e.get("Element") or "Item",
            "Unit": e.get("Unit") or "item",
            "Quantity": qty
        })

    if not cleaned_entries:
        print("❌ No BoQ entries found from any PDF.")
    else:
        print(f"✅ Found {len(cleaned_entries)} BoQ entries from all drawings.")
        # generate BESMM4 BoQ using the full template (adjust path if needed)
        #template_path = os.path.join(os.getcwd(), "qs_ai_project", "besmm4_template_full.csv")
        output_path = os.path.join(os.getcwd(), "besmm4_full_boq.xlsx")
        try:
            from boq_generator import generate_besmm4_boq
            generate_besmm4_boq(cleaned_entries, output_path, location=location)
            print(f"✅ BoQ exported to: {output_path}")
        except Exception as e:
            print(f"❌ generate_besmm4_boq failed: {e}")







