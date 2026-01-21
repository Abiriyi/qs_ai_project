from uuid import uuid4
from .models import ScottIssue, ScottSchedule, Position
from .evidence import collect_evidence
from .status_engine import determine_status


class ScottScheduleComposer:

    def compose(self, issue_seeds, contract_ref):
        issues = []

        for seed in issue_seeds:
            claimant_amount = seed["claimant_qty"] * seed["claimant_rate"]
            respondent_amount = seed["respondent_qty"] * seed["respondent_rate"]

            status = determine_status(claimant_amount, respondent_amount)

            agreed = min(claimant_amount, respondent_amount)
            disputed = max(0.0, claimant_amount - respondent_amount)

            issue = ScottIssue(
                issue_id=str(uuid4()),
                reference=seed["reference"],
                description=seed["description"],
                period=seed.get("period"),

                claimant=Position(
                    quantity=seed["claimant_qty"],
                    rate=seed["claimant_rate"],
                    amount=round(claimant_amount, 2),
                    basis=seed["claimant_basis"],
                    confidence=seed.get("claimant_confidence", 0.8),
                ),

                respondent=Position(
                    quantity=seed["respondent_qty"],
                    rate=seed["respondent_rate"],
                    amount=round(respondent_amount, 2),
                    basis=seed["respondent_basis"],
                    confidence=seed.get("respondent_confidence", 0.8),
                ),

                agreed_amount=round(agreed, 2),
                disputed_amount=round(disputed, 2),
                status=status,
                evidence_refs=collect_evidence(seed),
            )

            issues.append(issue)

        return ScottSchedule(
            schedule_id=str(uuid4()),
            contract_ref=contract_ref,
            issues=issues,
        )
