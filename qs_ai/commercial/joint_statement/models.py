from dataclasses import dataclass
from typing import Optional
from uuid import uuid4


@dataclass
class JointIssue:
    issue_id: str
    reference: str
    description: str

    claimant_position: float
    respondent_position: float

    agreed_position: Optional[float]
    disagreement_reason: Optional[str]

    status: str  # Agreed / Narrowed / Disagreed


@dataclass
class JointStatement:
    statement_id: str
    contract_ref: str
    issues: list[JointIssue]
