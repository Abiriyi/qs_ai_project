from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4


@dataclass
class Position:
    quantity: float
    rate: float
    amount: float
    basis: str
    confidence: float


@dataclass
class ScottIssue:
    issue_id: str
    reference: str
    description: str
    period: Optional[str]

    claimant: Position
    respondent: Position

    agreed_amount: float
    disputed_amount: float
    status: str

    evidence_refs: List[str] = field(default_factory=list)


@dataclass
class ScottSchedule:
    schedule_id: str
    contract_ref: str
    issues: List[ScottIssue]
