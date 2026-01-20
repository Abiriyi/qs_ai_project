from qs_ai.contracts.base import ContractBase

class NECContract(ContractBase):
    name = "NEC"

    def validate_notice(self, event):
        return event["notified"]

    def assess_entitlement(self, event):
        return {"entitled": True, "types": ["Compensation Event"]}

    def applicable_clauses(self, event_type):
        return []
