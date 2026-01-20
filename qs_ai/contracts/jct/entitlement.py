from qs_ai.contracts.base import ContractBase

class JCTContract(ContractBase):
    name = "JCT"

    def validate_notice(self, event):
        return True  # simplified (JCT more flexible)

    def assess_entitlement(self, event):
        return {"entitled": True, "types": ["Loss & Expense"]}

    def applicable_clauses(self, event_type):
        return []
