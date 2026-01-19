from dataclasses import dataclass
from .models import ClaimEvent

@dataclass
class EntitlementResult:
    entitled: bool
    time_entitlement_days: int
    cost_entitlement: bool
    reasoning: str

class EntitlementEngine:

    def assess(self, event: ClaimEvent) -> EntitlementResult:
        if event.event_type == "Variation":
            return EntitlementResult(
                entitled=True,
                time_entitlement_days=0,
                cost_entitlement=True,
                reasoning="Variation instructed by Engineer"
            )

        if event.event_type == "Delay" and event.caused_by == "Employer":
            return EntitlementResult(
                entitled=True,
                time_entitlement_days=14,
                cost_entitlement=True,
                reasoning="Employer-caused delay"
            )

        return EntitlementResult(
            entitled=False,
            time_entitlement_days=0,
            cost_entitlement=False,
            reasoning="No contractual entitlement"
        )

