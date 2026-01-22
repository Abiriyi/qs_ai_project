# qs_ai/tribunal/pdf_bundle/watermark.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


class PdfWatermark:

    def add_footer(self, output_path, footer_text):
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        c.setFont("Helvetica", 8)
        c.setFillGray(0.4)

        c.drawCentredString(
            width / 2,
            20,
            footer_text
        )

        c.showPage()
        c.save()
