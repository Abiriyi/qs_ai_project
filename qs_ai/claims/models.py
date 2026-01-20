# qs_ai/claims/models.py
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional
from uuid import uuid4


@dataclass(frozen=True)
class ClaimEvent:
    event_id: str
    event_type: str              # Variation | Delay | Disruption | Instruction
    description: str
    cause: str                   # Employer | Engineer | Force Majeure | Contractor
    start_date: date
    end_date: Optional[date]
    contract_clause: Optional[str]
    notified: bool
    notification_date: Optional[date]


@dataclass(frozen=True)
class ClaimEntitlement:
    event_id: str
    entitlement_type: str        # EOT | Loss & Expense | Prolongation | Variation
    days_entitled: Optional[int]
    cost_entitled: Optional[float]
    basis: str                   # Contractual / Common law
    justification: str


@dataclass(frozen=True)
class ClaimLine:
    line_id: str
    description: str
    amount: float
    basis: str                   # QS valuation / productivity loss / prolongation


@dataclass(frozen=True)
class ClaimPackage:
    claim_id: str
    project_name: str
    contractor: str
    employer: str
    contract_form: str
    submission_date: date

    events: List[ClaimEvent]
    entitlements: List[ClaimEntitlement]
    claim_lines: List[ClaimLine]

    total_claim_value: float
    narrative_summary: str

    prepared_by: str
    approved_by: Optional[str] = None
    approval_date: Optional[date] = None
