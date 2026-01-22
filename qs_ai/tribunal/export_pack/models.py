# qs_ai/tribunal/export_pack/models.py
from dataclasses import dataclass
from typing import List
from datetime import datetime


@dataclass(frozen=True)
class EvidenceItem:
    ref: str
    description: str
    source: str
    file_path: str


@dataclass(frozen=True)
class TribunalExportPack:
    pack_id: str
    contract_reference: str
    prepared_at: datetime
    prepared_by: str
    documents: List[str]
    evidence: List[EvidenceItem]
    hash_manifest_path: str
