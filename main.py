from pdf_parser import extract_pdf_text
from boq_generator import generate_boq_excel

if __name__ == "__main__":
    pdf_path = "assets/sample_drawing.pdf"

    location = input("Enter project location for pricing (e.g., Nairobi): ").strip()

    output = extract_pdf_text(pdf_path)
    generate_boq_excel(output, "boq_output.xlsx", location)

    print("✅ BoQ generated with location-specific pricing.")