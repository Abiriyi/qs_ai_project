# qs_ai/tribunal/pdf_bundle/builder.py
from qs_ai.tribunal.pdf_bundle.bundle_renderer import TribunalPdfBundleRenderer


class TribunalPdfBundleBuilder:

    def build(self, sections, output_path):
        renderer = TribunalPdfBundleRenderer()
        toc_entries = renderer.render(sections, output_path)
        return toc_entries
