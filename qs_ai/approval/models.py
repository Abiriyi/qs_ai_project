from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Optional

class JointApprovalStatus(str, Enum):
    DRAFT = "DRAFT"
    SIGNED_BY_EXPERT_A = "SIGNED_BY_EXPERT_A"
    SIGNED_BY_EXPERT_B = "SIGNED_BY_EXPERT_B"
    FULLY_SIGNED = "FULLY_SIGNED"

class ApprovalStatus(Enum):
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

@dataclass(frozen=True)
class ExpertApproval:
    approval_id: str
    artefact_type: str
    artefact_id: str
    approved_by: str
    approved_role: str
    approval_datetime: datetime
    status: ApprovalStatus
    digital_signature: Optional[str] = None
    remarks: Optional[str] = None
@dataclass(frozen=True)
class JointExpertSignature:
    expert_id: str
    name: str
    role: str
    organisation: str
    signed_at: datetime
    digital_signature: str

