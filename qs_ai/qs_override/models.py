from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass(frozen=True)
class QSOverrideRecord:
    override_id: str = field(default_factory=lambda: str(uuid4()))

    # Identification
    boq_item_code: str = ""
    description: str = ""

    # Quantities
    base_quantity: float = 0.0
    overridden_quantity: float = 0.0
    unit: str = ""

    # QS Justification
    reason: str = ""
    technical_basis: Optional[str] = None

    # Authority & provenance
    created_by: str = ""
    created_role: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Approval workflow
    approval_state: str = "DRAFT"

    def delta(self) -> float:
        return round(self.overridden_quantity - self.base_quantity, 6)


