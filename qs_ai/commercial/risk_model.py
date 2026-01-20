# qs_ai/commercial/risk_model.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class CostRisk:
    risk_id: str
    description: str
    boq_item_ref: Optional[str]      # e.g. "D20 Plastering"
    probability: float               # 0.0 – 1.0
    cost_impact: float               # monetary value
    mitigation: Optional[str]
    owner: str                        # QS / PM / Contractor
