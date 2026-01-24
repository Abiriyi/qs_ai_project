# qs_ai/tribunal/pdf_bundle/bundle_builder.py

from reportlab.platypus import SimpleDocTemplate, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from pathlib import Path

from qs_ai.tribunal.pdf_bundle.section_renderers import (
    render_cover,
    render_index,
    render_scott_schedule,
    render_expert_statement,
    render_evidence_register,
)
from qs_ai.tribunal.pdf_bundle.index_builder import IndexBuilder


class TribunalBundleBuilder:
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.story = []
        self.index = IndexBuilder()

    def build(self, payload: dict):
        """
        payload must include:
        - case_metadata
        - scott_schedule
        - expert_statement
        - evidence_register
        """

        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=25 * mm,
            bottomMargin=25 * mm,
        )

        # ---- Sections (order matters) ----
        render_cover(self.story, payload["case_metadata"], self.index)
        self.story.append(PageBreak())

        render_index(self.story, self.index)
        self.story.append(PageBreak())

        render_scott_schedule(self.story, payload["scott_schedule"], self.index)
        self.story.append(PageBreak())

        render_expert_statement(self.story, payload["expert_statement"], self.index)
        self.story.append(PageBreak())

        render_evidence_register(self.story, payload["evidence_register"], self.index)

        doc.build(self.story)
        return self.output_path
