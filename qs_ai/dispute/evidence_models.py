from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class EvidenceItem:
    reference: str
    description: str
    source: str            # drawing, letter, programme
    date: str
    verified: bool


@dataclass(frozen=True)
class ExpertFinding:
    fact: str
    evidence_refs: List[str]


@dataclass(frozen=True)
class ExpertOpinion:
    opinion: str
    methodology: str
    assumptions: List[str]
    confidence_level: float
