from pdf_parser import extract_pdf_text
from boq_generator import generate_boq_excel

if __name__ == "__main__":
    pdf_path = "assets/floorplan.pdf"
    room_data = extract_pdf_text(pdf_path)

    print("\n📏 Room Areas:")
    for r in room_data:
        print(f"{r['room']} — {r['area_m2']} m² (L: {r['length_mm']} mm, W: {r['width_mm']} mm)")

    # Generate Excel BoQ
    generate_boq_excel(room_data)
