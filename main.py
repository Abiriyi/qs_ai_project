from pdf_parser import extract_pdf_text
from parse_floorplan import build_boq_entries
from boq_generator import generate_boq_excel

if __name__ == "__main__":
    pdf_files = [
        ("assets/floorplan.pdf", "boq_output_floorplan.xlsx"),
        ("assets/Section_X-X.pdf", "boq_output_section_x-x.xlsx")
    ]
    location = input("Enter project location for pricing (e.g., Nairobi): ").strip()

    for pdf_path, output_file in pdf_files:
        # Step 1: Extract rooms + measurements
        rooms_data = extract_pdf_text(pdf_path)

        # Step 2: Build BoQ entries with all keys
        boq_entries = build_boq_entries(rooms_data)

        # Step 3: Generate BoQ Excel
        generate_boq_excel(boq_entries, output_file, location)

        print(f"✅ BoQ generated for {pdf_path} with location-specific pricing.")