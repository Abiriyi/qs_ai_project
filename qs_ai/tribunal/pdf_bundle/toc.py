# qs_ai/tribunal/pdf_bundle/toc.py
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet


class TableOfContentsBuilder:

    def build(self, toc_entries):
        styles = getSampleStyleSheet()
        content = [Paragraph("<b>Table of Contents</b>", styles["Heading1"])]

        for entry in toc_entries:
            content.append(
                Paragraph(
                    f"{entry['title']} .......... {entry['start_page']}",
                    styles["Normal"],
                )
            )

        return content
