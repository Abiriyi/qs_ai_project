from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    category: str                # geometry | override | approval | claim
    source: str                  # module / rule name
    description: str
    payload: Dict[str, Any]      # raw evidence data
    content_hash: str
    created_at: datetime
    created_by: Optional[str] = None
