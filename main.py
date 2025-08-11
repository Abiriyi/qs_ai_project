from pdf_parser import extract_pdf_text
from parse_floorplan import build_boq_entries
from boq_generator import generate_boq_excel
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    pdf_files = [
        "assets/floorplan.pdf",
        "assets/Section_X-X.pdf",
        "assets/Doors and windows schedule.pdf"
    ]

    location = input("Enter project location for pricing (e.g., Nairobi): ").strip()

    merged_data = {
        "rooms": [],
        "heights": [],
        "openings": []
    }

    for pdf_path in pdf_files:
        print(f"📄 Processing {pdf_path} ...")
        parsed_data = extract_pdf_text(pdf_path)

        # Merge parsed results
        merged_data["rooms"].extend(parsed_data.get("rooms", []))
        merged_data["heights"].extend(parsed_data.get("heights", []))
        merged_data["openings"].extend(parsed_data.get("openings", []))

    if not merged_data["rooms"] and not merged_data["heights"]:
        print("❌ No usable data found in any PDF.")
    else:
        boq_entries = build_boq_entries(merged_data)
        if boq_entries:
            print(f"✅ Generated {len(boq_entries)} BoQ entries.")
            generate_boq_excel(boq_entries, "boq_output.xlsx")
            print("📄 BoQ saved to boq_output.xlsx")
        else:
            print("⚠️ No BoQ entries generated from parsed data.")
