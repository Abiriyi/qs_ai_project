from datetime import datetime
from uuid import uuid4
from .models import FinalAccount, FinalAccountLine
from .exceptions import FinalAccountNotApprovedError


class FinalAccountEngine:

    def prepare_final_account(self, boq_items, adjustments, contract_id):
        """
        boq_items: list of BoQ lines
        adjustments: list of Adjustment objects
        """

        lines = []

        for item in boq_items:
            item_adjustments = [
                a for a in adjustments if a.boq_item_code == item["ItemCode"]
            ]

            line = FinalAccountLine(
                boq_item_code=item["ItemCode"],
                description=item["Description"],
                original_quantity=item["Quantity"],
                original_rate=item["Rate"],
                original_value=item["Quantity"] * item["Rate"],
                adjustments=item_adjustments,
            )
            lines.append(line)

        return FinalAccount(
            final_account_id=str(uuid4()),
            contract_id=contract_id,
            lines=lines,
            approval_state="DRAFT",
            created_at=datetime.utcnow(),
        )

    def close_final_account(self, final_account):
        if final_account.approval_state != "EMPLOYER APPROVED":
            raise FinalAccountNotApprovedError(
                "Final Account must be employer-approved before closure"
            )

        final_account.approval_state = "FINAL ACCOUNT CLOSED"
        return final_account
