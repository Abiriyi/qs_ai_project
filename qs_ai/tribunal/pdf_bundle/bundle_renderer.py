# qs_ai/tribunal/pdf_bundle/bundle_renderer.py
from PyPDF2 import PdfMerger
from qs_ai.tribunal.pdf_bundle.paginator import PageTracker


class TribunalPdfBundleRenderer:

    def render(self, sections, output_path):
        merger = PdfMerger()
        tracker = PageTracker()

        for section in sections:
            merger.append(section["path"])
            tracker.add_section(
                section["title"],
                section["page_count"],
            )

        merger.write(output_path)
        merger.close()

        return tracker.entries
