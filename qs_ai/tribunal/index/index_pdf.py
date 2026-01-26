from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from pathlib import Path


def generate_index_pdf(entries, output_path: Path):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)

    elements = [
        Paragraph("<b>Tribunal Document Index</b>", styles["Title"]),
        Paragraph("Automatically generated index of submitted materials.", styles["Normal"]),
    ]

    table_data = [[
        "Doc ID", "Title", "Category", "Date", "Version", "Pages", "File", "SHA-256"
    ]]

    for e in entries:
        table_data.append([
            e.doc_id,
            e.title,
            e.category,
            e.document_date.isoformat(),
            e.version,
            str(e.page_count),
            e.file_name,
            e.sha256[:16] + "...",
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(table)
    doc.build(elements)
