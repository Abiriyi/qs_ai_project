# qs_ai/tribunal/pdf_bundle/page_seal.py
from PyPDF2 import PdfReader, PdfWriter
from qs_ai.tribunal.pdf_bundle.footer_text import build_footer_text
from qs_ai.tribunal.pdf_bundle.watermark import PdfWatermark
import tempfile
import os


class PageSealer:

    def seal_pages(self, source_pdf, output_pdf, version, sha256):
        reader = PdfReader(source_pdf)
        writer = PdfWriter()

        total_pages = len(reader.pages)

        for i, page in enumerate(reader.pages, start=1):
            footer = build_footer_text(
                version=version,
                sha256=sha256,
                page=i,
                total_pages=total_pages,
            )

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            PdfWatermark().add_footer(tmp.name, footer)

            footer_pdf = PdfReader(tmp.name)
            page.merge_page(footer_pdf.pages[0])
            writer.add_page(page)

            os.unlink(tmp.name)

        with open(output_pdf, "wb") as f:
            writer.write(f)
