from uuid import uuid4
from .models import JointIssue, JointStatement
from .agreement_engine import assess_agreement


class JointStatementComposer:

    def compose(self, scott_schedule, contract_ref):
        issues = []

        for issue in scott_schedule.issues:
            status, agreed, reason = assess_agreement(
                issue.claimant.amount,
                issue.respondent.amount,
            )

            joint_issue = JointIssue(
                issue_id=issue.issue_id,
                reference=issue.reference,
                description=issue.description,
                claimant_position=issue.claimant.amount,
                respondent_position=issue.respondent.amount,
                agreed_position=agreed if status != "Disagreed" else None,
                disagreement_reason=reason if status != "Agreed" else None,
                status=status,
            )

            issues.append(joint_issue)

        return JointStatement(
            statement_id=str(uuid4()),
            contract_ref=contract_ref,
            issues=issues,
        )
