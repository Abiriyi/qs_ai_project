# qs_ai/tribunal/pdf_bundle/section_renderers.py

from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

styles = getSampleStyleSheet()


def _h(text):
    return Paragraph(f"<b>{text}</b>", styles["Heading2"])


def _p(text):
    return Paragraph(text, styles["Normal"])


def render_cover(story, metadata, index):
    index.register("Cover Page")
    story.append(_h("TRIBUNAL DOCUMENT BUNDLE"))
    story.append(Spacer(1, 12))
    for k, v in metadata.items():
        story.append(_p(f"<b>{k}:</b> {v}"))


def render_index(story, index):
    story.append(_h("Document Index"))
    for entry in index.entries:
        story.append(_p(entry))


def render_scott_schedule(story, schedule, index):
    index.register("Scott Schedule")
    story.append(_h("Scott Schedule"))

    table_data = [["Issue", "Claimant", "Respondent", "QS Opinion"]]
    for row in schedule:
        table_data.append([
            row["issue"],
            row["claimant_position"],
            row["respondent_position"],
            row["qs_opinion"],
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]))
    story.append(table)


def render_expert_statement(story, statement, index):
    index.register("Expert Statement")
    story.append(_h("Independent QS Expert Statement"))
    for para in statement:
        story.append(_p(para))
        story.append(Spacer(1, 10))


def render_evidence_register(story, register, index):
    index.register("Evidence Register")
    story.append(_h("Evidence Register"))

    for e in register:
        story.append(_p(f"{e['ref']}: {e['description']}"))
