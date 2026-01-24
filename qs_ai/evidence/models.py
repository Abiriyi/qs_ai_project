from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass(frozen=True)
class EvidenceArtifact:
    evidence_id: str
    category: str            # geometry | override | approval | contract | correspondence
    source: str              # module / rule / document origin
    description: str
    payload: Dict[str, Any]
    created_by: str
    created_at: datetime

