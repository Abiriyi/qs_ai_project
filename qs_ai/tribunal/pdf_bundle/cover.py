# qs_ai/tribunal/pdf_bundle/cover.py
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def build_cover(path, title, subtitle, prepared_by):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path)

    content = [
        Paragraph(f"<b>{title}</b>", styles["Title"]),
        Paragraph(subtitle, styles["Normal"]),
        Paragraph(f"Prepared by: {prepared_by}", styles["Normal"]),
    ]

    doc.build(content)
