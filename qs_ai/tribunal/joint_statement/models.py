# qs_ai/tribunal/joint_statement/models.py
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass(frozen=True)
class JointStatementIssue:
    issue_id: str
    description: str
    claimant_position: str
    respondent_position: str
    agreed: bool
    agreed_amount: Optional[float]
    disagreement_reason: Optional[str]


@dataclass(frozen=True)
class ExpertSignature:
    expert_name: str
    firm: str
    role: str  # Claimant / Respondent / Tribunal-appointed
    signed_at: datetime
    digital_fingerprint: str


@dataclass(frozen=True)
class JointExpertStatement:
    statement_id: str
    contract_reference: str
    prepared_at: datetime
    issues: List[JointStatementIssue]
    claimant_expert: Optional[ExpertSignature]
    respondent_expert: Optional[ExpertSignature]
    locked: bool
