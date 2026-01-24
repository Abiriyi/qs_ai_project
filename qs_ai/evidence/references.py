from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceReference:
    artefact_id: str          # Scott issue / BoQ item / valuation line
    evidence_id: str
    relevance: str            # primary | supporting | contextual
