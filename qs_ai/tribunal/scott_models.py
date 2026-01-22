# qs_ai/tribunal/scott_models.py
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass(frozen=True)
class ScottIssue:
    issue_id: str
    description: str
    claimant_position: str
    respondent_position: Optional[str] = None


@dataclass(frozen=True)
class ScottQuantityReference:
    bound_quantity_id: str


@dataclass(frozen=True)
class ScottItem:
    item_id: str
    issue: ScottIssue
    quantity_ref: ScottQuantityReference
    rate: float
    claimed_amount: float
    confidence: float
    approval_snapshot_id: str


@dataclass(frozen=True)
class ScottSchedule:
    schedule_id: str
    title: str
    contract_reference: str
    prepared_by: str
    prepared_at: datetime
    items: List[ScottItem]
