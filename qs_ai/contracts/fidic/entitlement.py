# qs_ai/contracts/fidic/entitlement.py
from qs_ai.contracts.base import ContractBase
from qs_ai.contracts.fidic.notice_rules import notice_valid
from qs_ai.contracts.fidic.clauses import CLAUSES


class FIDICContract(ContractBase):

    name = "FIDIC"

    def validate_notice(self, event):
        return notice_valid(event)

    def assess_entitlement(self, event):
        if not self.validate_notice(event):
            return {
                "entitled": False,
                "reason": "Late or missing notice under Clause 20.1",
            }

        if event["cause"] == "Employer":
            return {
                "entitled": True,
                "types": ["EOT", "Loss & Expense"],
            }

        return {
            "entitled": False,
            "reason": "No employer risk event",
        }

    def applicable_clauses(self, event_type: str):
        return CLAUSES.get(event_type, [])
