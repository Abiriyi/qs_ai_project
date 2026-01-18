from dataclasses import dataclass
from datetime import date
from typing import List, Optional

@dataclass(frozen=True)
class VariationItem:
    item_id: str
    description: str
    quantity: float
    unit: str
    unit_rate: float
    rate_source: str  # "contract", "star", "new"
    justification: str

    @property
    def value(self) -> float:
        return round(self.quantity * self.unit_rate, 2)

@dataclass(frozen=True)
class VariationOrder:
    vo_id: str
    instruction_ref: str
    description: str
    issued_date: date
    valued_by: str
    items: List[VariationItem]
    status: str  # DRAFT, QS_VALUED, APPROVED, CERTIFIED
