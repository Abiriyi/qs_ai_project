from dataclasses import dataclass
from typing import List


@dataclass
class TribunalPack:
    project_id: str
    claims: List
    approvals: List
    evidence: List
    status: str
    system_release: str
