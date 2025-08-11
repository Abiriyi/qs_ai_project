from pdf_parser import extract_pdf_text
from parse_floorplan import build_boq_entries
from boq_generator import generate_boq_excel
from parse_opening_schedule import parse_opening_schedule
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Main architectural + section drawings
    pdf_files = [
        "assets/floorplan.pdf",
        "assets/Section_X-X.pdf"
    ]

    # Doors & windows schedule PDF
    openings_schedule_pdf = "assets/Doors and windows schedule.pdf"

    location = input("Enter project location for pricing (e.g., Nairobi): ").strip()
    all_boq_entries = []

    # Parse openings schedule
    print(f"📄 Parsing openings schedule: {openings_schedule_pdf} ...")
    openings_lib = parse_opening_schedule(openings_schedule_pdf, verbose=True)

    # Process each architectural / section PDF
    for pdf_path in pdf_files:
        print(f"📄 Processing {pdf_path} ...")
        parsed_data = extract_pdf_text(pdf_path)

        if not parsed_data["rooms"] and not parsed_data["heights"]:
            print(f"⚠️ No data detected in {pdf_path}. Skipping...")
            continue

        # Merge openings_lib into parsed_data["openings"]
        # Convert openings_lib (dict) into list format expected by build_boq_entries
        openings_list = []
        for tag, data in openings_lib.items():
            openings_list.append({
                "tag": tag,
                "count": data["count"],
                "width_m": data["width_m"],
                "height_m": data["height_m"],
                "x": 0,  # Schedule doesn’t give coordinates
                "y": 0,
                "page": 1  # Default to page 1 for now
            })

        parsed_data["openings"].extend(openings_list)

        # Build BoQ entries from this PDF's parsed data
        boq_entries = build_boq_entries(parsed_data)
        all_boq_entries.extend(boq_entries)

    if not all_boq_entries:
        print("❌ No BoQ entries found from any PDF.")
    else:
        print(f"✅ Found {len(all_boq_entries)} BoQ entries from all drawings.")
        generate_boq_excel(all_boq_entries, "boq_output.xlsx", location)


