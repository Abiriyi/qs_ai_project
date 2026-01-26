# qs_ai/tribunal/models.py
from dataclasses import dataclass
from typing import List


@dataclass
class TribunalPack:
    claim_id: str
    approvals: List
    evidence: List
    status: str
