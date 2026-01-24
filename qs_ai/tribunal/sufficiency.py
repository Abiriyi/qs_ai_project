from dataclasses import dataclass
from typing import List


@dataclass
class EvidenceCheckResult:
    artefact_id: str
    sufficient: bool
    missing: List[str]
    warnings: List[str]
