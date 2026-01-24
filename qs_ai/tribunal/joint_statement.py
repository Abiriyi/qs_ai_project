from dataclasses import dataclass, field
from typing import List
from qs_ai.approval.models import JointApprovalStatus, JointExpertSignature


@dataclass
class JointStatement:
    statement_id: str
    artefact_id: str  # Scott Schedule / issue bundle
    status: JointApprovalStatus
    signatures: List[JointExpertSignature] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)