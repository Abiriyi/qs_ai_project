from pdf_parser import extract_pdf_text
from parse_floorplan import build_boq_entries
from boq_generator import generate_boq_excel

if __name__ == "__main__":
    pdf_path = "assets/floorplan.pdf"
    location = input("Enter project location for pricing (e.g., Abuja): ").strip()

    # Step 1: Extract rooms + measurements
    rooms_data = extract_pdf_text(pdf_path)

    # Step 2: Build BoQ entries with all keys
    boq_entries = build_boq_entries(rooms_data)

    # Step 3: Generate BoQ Excel
    generate_boq_excel(boq_entries, "boq_output.xlsx", location)

    print("✅ BoQ generated with location-specific pricing.")
