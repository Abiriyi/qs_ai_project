from dataclasses import dataclass
from datetime import date
from typing import List

@dataclass(frozen=True)
class ValuationLine:
    boq_item_id: str
    tender_quantity: float
    executed_quantity_to_date: float
    unit_rate: float

    @property
    def value_to_date(self) -> float:
        return round(self.executed_quantity_to_date * self.unit_rate, 2)

@dataclass(frozen=True)
class Valuation:
    valuation_id: str
    snapshot_id: str
    valuation_no: int
    valuation_date: date
    prepared_by: str
    lines: List[ValuationLine]
    retention_percent: float
