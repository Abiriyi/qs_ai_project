from pdf_parser import extract_pdf_text
from parse_floorplan import build_boq_entries
from boq_generator import generate_boq_excel
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    pdf_files = [
        "assets/floorplan.pdf",
        "assets/Section_X-X.pdf"
    ]

    location = input("Enter project location for pricing (e.g., Nairobi): ").strip()
    all_boq_entries = []

    for pdf_path in pdf_files:
        print(f"📄 Processing {pdf_path} ...")
        parsed_data = extract_pdf_text(pdf_path)

        if not parsed_data["rooms"] and not parsed_data["heights"]:
            print(f"⚠️ No data detected in {pdf_path}. Skipping...")
            continue

        boq_entries = build_boq_entries(parsed_data)
        all_boq_entries.extend(boq_entries)

    if not all_boq_entries:
        print("❌ No BoQ entries found from any PDF.")
    else:
        print(f"✅ Found {len(all_boq_entries)} BoQ entries from all drawings.")
        generate_boq_excel(all_boq_entries, "boq_output.xlsx", location)
