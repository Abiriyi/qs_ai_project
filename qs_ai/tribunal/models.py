from dataclasses import dataclass
from typing import List
from qs_ai.system.fingerprint import dependency_fingerprint

@dataclass
class TribunalPack:
    project_id: str
    claims: List
    approvals: List
    evidence: List
    status: str
    system_release: str
