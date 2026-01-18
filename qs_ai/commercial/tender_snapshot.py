from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class TenderSnapshot:
    snapshot_id: str
    boq_id: str
    revision: int
    issued_by: str
    issued_at: datetime
    purpose: str                 # IFT | RFP | Negotiation
    currency: str
    locked: bool = True
    notes: Optional[str] = None
