from dataclasses import dataclass, field
from typing import List
from uuid import uuid4
from datetime import datetime


@dataclass(frozen=True)
class Adjustment:
    adjustment_id: str
    boq_item_code: str
    adjustment_type: str  # VARIATION | REMEASUREMENT | OMISSION | PROVISIONAL
    quantity_delta: float
    rate: float
    value: float
    approved_by: str
    approval_date: datetime
    reference: str  # VO number, instruction, etc.


@dataclass
class FinalAccountLine:
    boq_item_code: str
    description: str
    original_quantity: float
    original_rate: float
    original_value: float

    adjustments: List[Adjustment] = field(default_factory=list)

    @property
    def final_quantity(self) -> float:
        return self.original_quantity + sum(a.quantity_delta for a in self.adjustments)

    @property
    def final_value(self) -> float:
        return self.original_value + sum(a.value for a in self.adjustments)


@dataclass
class FinalAccount:
    final_account_id: str
    contract_id: str
    lines: List[FinalAccountLine]
    approval_state: str  # DRAFT → FINAL ACCOUNT CLOSED
    created_at: datetime
