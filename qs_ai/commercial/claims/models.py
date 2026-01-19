from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class ClaimEvent:
    event_id: str
    event_type: str            # Variation | Delay | Disruption | Omission
    description: str
    notice_date: date
    instruction_ref: Optional[str]
    caused_by: str             # Employer | Contractor | Neutral
    contract_clause: str       # e.g. "FIDIC 20.1"
