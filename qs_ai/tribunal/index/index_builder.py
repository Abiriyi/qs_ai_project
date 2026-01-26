from datetime import date
from pathlib import Path
from qs_ai.tribunal.index.models import TribunalIndexEntry


def build_index_entries(file_hashes: dict) -> list[TribunalIndexEntry]:
    """
    Build Tribunal Index entries from hashed files.
    """
    entries = []
    counter = 1

    for file_name, sha in file_hashes.items():
        entries.append(
            TribunalIndexEntry(
                doc_id=f"D{counter:03}",
                title=Path(file_name).stem.replace("_", " "),
                category=_infer_category(file_name),
                document_date=date.today(),
                version="1.0",
                page_count=0,  # populated later if PDF
                file_name=file_name,
                sha256=sha,
            )
        )
        counter += 1

    return entries


def _infer_category(file_name: str) -> str:
    name = file_name.lower()
    if "scott" in name:
        return "Scott Schedule"
    if "report" in name:
        return "Expert Report"
    if "drawing" in name or name.endswith(".dwg"):
        return "Drawing"
    if name.endswith(".pdf"):
        return "PDF Evidence"
    return "Supporting Document"
