from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class JointApprovalStatus(str, Enum):
    DRAFT = "DRAFT"
    SIGNED_BY_EXPERT_A = "SIGNED_BY_EXPERT_A"
    SIGNED_BY_EXPERT_B = "SIGNED_BY_EXPERT_B"
    FULLY_SIGNED = "FULLY_SIGNED"


@dataclass(frozen=True)
class JointExpertSignature:
    expert_id: str
    name: str
    role: str
    organisation: str
    signed_at: datetime
    digital_signature: str

