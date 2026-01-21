from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ApprovalStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    SEALED = "sealed"


@dataclass(frozen=True)
class ExpertApproval:
    approval_id: str
    artefact_type: str          # "boq", "valuation", "claim", "certificate"
    artefact_id: str
    approved_by: str            # QS / Expert name
    approved_role: str          # "Commercial Manager", "Expert Witness"
    approval_datetime: datetime
    status: ApprovalStatus
    remarks: Optional[str] = None
    digital_signature: Optional[str] = None
