from dataclasses import dataclass
from qs_ai.commercial.claims.entitlement import EntitlementResult

@dataclass 
class ClaimValuation:
    event_id: str
    time_days: int
    cost_amount: float
    valuation_basis: str

class ClaimValuationEngine:

    def value(self, entitlement: EntitlementResult, rates):
        if not entitlement.entitled:
            return None

        cost = 0.0
        if entitlement.cost_entitlement:
            cost = rates.get("preliminaries_daily", 0) * entitlement.time_entitlement_days

        return ClaimValuation(
            event_id="",
            time_days=entitlement.time_entitlement_days,
            cost_amount=round(cost, 2),
            valuation_basis="Time-related preliminaries"
        )
