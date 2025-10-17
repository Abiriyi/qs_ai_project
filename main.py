# main.py
import os
from dotenv import load_dotenv

from pdf_parser import extract_pdf_text
from parse_floorplan import build_boq_entries
from parse_section import parse_section as parse_section_pdf
from parse_opening_schedule import parse_opening_schedule
from boq_generator import generate_boq_excel, WORKSECTIONS_ORDER, pluralize_worksection

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
    # input document list (you can modify)
    pdf_files = [
        "assets/floorplan.pdf",
        "assets/Section_X-X.pdf"
    ]
    openings_schedule_pdf = "assets/Doors and windows schedule.pdf"

    location = input("Enter project location for pricing (e.g., Abuja): ").strip()
    all_boq_entries = []

    # 1) Openings schedule (may return tuple or dict depending on version)
    print(f"📄 Parsing openings schedule: {openings_schedule_pdf} ...")
    openings_result = parse_opening_schedule(openings_schedule_pdf, verbose=True)

    # handle both return styles: dict or (dict, list)
    if isinstance(openings_result, tuple) and len(openings_result) >= 1:
        openings_lib = openings_result[0] or {}
        opening_boq_entries = openings_result[1] if len(openings_result) > 1 else []
    else:
        openings_lib = openings_result or {}
        opening_boq_entries = []

    # Add BoQ entries produced directly by the openings schedule parser (if any)
    if opening_boq_entries:
        all_boq_entries.extend(opening_boq_entries)

    # Keep normalized list for injecting into parsed_data for rooms
    openings_list_from_schedule = normalize_openings_lib(openings_lib)

    # 2) Process each architectural/section PDF
    for pdf_path in pdf_files:
        print(f"📄 Processing {pdf_path} ...")
        if not os.path.exists(pdf_path):
            print(f"⚠️ File not found: {pdf_path} — skipping.")
            continue

        # If the file looks like a SECTION drawing, parse structural info from it
        if "section" in os.path.basename(pdf_path).lower():
            # parse_section_pdf returns a list of BoQ-like dicts
            try:
                section_entries = parse_section_pdf(pdf_path, verbose=True)
                if section_entries:
                    all_boq_entries.extend(section_entries)
                    print(f"   → Added {len(section_entries)} entries from section parser.")
            except Exception as e:
                print(f"   ⚠️ parse_section failed for {pdf_path}: {e}")
            # still also extract text for rooms if there are any (some section PDFs include rooms)
            parsed_data = extract_pdf_text(pdf_path)
        else:
            # normal floorplan / elevation / general drawing
            parsed_data = extract_pdf_text(pdf_path)

        # Merge openings from schedule into parsed_data openings (so room-level parser can deduct)
        parsed_data.setdefault("openings", [])
        # extend only unique tags (avoid duplicates)
        parsed_data["openings"].extend(openings_list_from_schedule)

        # If pdf_parser produced heuristic "others" entries, add them
        others = parsed_data.get("others") or []
        for other in others:
            # ensure it matches minimal BoQ entry shape
            if isinstance(other, dict) and other.get("Element"):
                all_boq_entries.append({
                    "Room": other.get("Room"),
                    "Element": other.get("Element"),
                    "Description": other.get("Description") or other.get("Element"),
                    "Unit": other.get("Unit") or "item",
                    "Quantity": other.get("Quantity") or 1
                })

        # Build room-based BoQ entries (finishes, fittings implied by room type, openings assigned to rooms)
        try:
            room_entries = build_boq_entries(parsed_data)
            if room_entries:
                all_boq_entries.extend(room_entries)
                print(f"   → Added {len(room_entries)} room-based entries.")
        except Exception as e:
            print(f"   ⚠️ build_boq_entries failed for {pdf_path}: {e}")

    # 3) Final guard: ensure entries are well-formed (Element, Description, Unit, Quantity)
    cleaned_entries = []
    for e in all_boq_entries:
        # normalize keys (support both "Qty" or "Quantity")
        qty = e.get("Quantity", e.get("Qty", 0))
        if qty is None:
            qty = 0
        cleaned_entries.append({
            "Room": str(e.get("Room") or ""),  # ensure always a string
            "Element": e.get("Element") or e.get("WorkSection") or "Misc",
            "Description": e.get("Description") or e.get("Element") or "Item",
            "Unit": e.get("Unit") or "item",
            "Quantity": qty
        })


    if not cleaned_entries:
        print("❌ No BoQ entries found from any PDF.")
    else:
        print(f"✅ Found {len(cleaned_entries)} BoQ entries from all drawings.")

        # 4) Provide a quick console summary by work section (using TRADE_MAP / pluralize)
        section_counts = {}
        for ent in cleaned_entries:
            # Map element -> trade and pluralize
            ws = pluralize_worksection( ( (ent.get("Element") or "").strip() ) )
            section_counts[ws] = section_counts.get(ws, 0) + 1

        print("BoQ counts by Work Section:")
        for ws in WORKSECTIONS_ORDER:
            print(f" - {ws}: {section_counts.get(ws, 0)}")
        # print any unmapped
        unmapped = {k:v for k,v in section_counts.items() if k not in WORKSECTIONS_ORDER}
        if unmapped:
            print(" - Other/Unclassified:", unmapped)

        # 5) Order entries by WORKSECTIONS_ORDER so excel uses consistent order
        # prepare a map: worksection -> list(entries)
        ordered_map = {ws: [] for ws in WORKSECTIONS_ORDER}
        other_bucket = []

        # We need to decide worksection for each cleaned entry (use TRADE_MAP inside generator.prepare_boq_entries,
        # but to order we need to approximate here: reuse pluralize_worksection on TRADE_MAP mapping)
        from boq_generator import TRADE_MAP  # import here to map element->section

        for ent in cleaned_entries:
            element = ent.get("Element", "")
            trade_section = TRADE_MAP.get(element, "General Works")
            plural_ws = pluralize_worksection(trade_section)
            if plural_ws in ordered_map:
                ordered_map[plural_ws].append(ent)
            else:
                other_bucket.append(ent)

        # flatten in order
        final_ordered_entries = []
        for ws in WORKSECTIONS_ORDER:
            final_ordered_entries.extend(ordered_map.get(ws, []))
        # append others last
        final_ordered_entries.extend(other_bucket)

        # 6) Export both versions (plain + styled)
        generate_boq_excel(final_ordered_entries, "boq_plain.xlsx", location, mode="plain")
        generate_boq_excel(final_ordered_entries, "boq_styled.xlsx", location, mode="styled")





