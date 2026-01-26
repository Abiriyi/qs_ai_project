from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class TribunalIndexEntry:
    doc_id: str
    title: str
    category: str
    document_date: date
    version: str
    page_count: int
    file_name: str
    sha256: str
    uploaded_by: str
    uploaded_at: datetime