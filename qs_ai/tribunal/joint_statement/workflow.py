# qs_ai/tribunal/joint_statement/workflow.py
from uuid import uuid4
from datetime import datetime
from qs_ai.tribunal.joint_statement.models import JointExpertStatement
from qs_ai.tribunal.joint_statement.exceptions import StatementLockedError


class JointStatementWorkflow:

    def create(self, contract_reference, issues):
        return JointExpertStatement(
            statement_id=str(uuid4()),
            contract_reference=contract_reference,
            prepared_at=datetime.utcnow(),
            issues=issues,
            claimant_expert=None,
            respondent_expert=None,
            locked=False,
        )

    def assert_unlocked(self, statement):
        if statement.locked:
            raise StatementLockedError("Joint statement is locked")

    def attach_claimant_signature(self, statement, signature):
        self.assert_unlocked(statement)
        return statement.__class__(
            **{**statement.__dict__, "claimant_expert": signature}
        )

    def attach_respondent_signature(self, statement, signature):
        self.assert_unlocked(statement)
        return statement.__class__(
            **{**statement.__dict__, "respondent_expert": signature}
        )

    def lock(self, statement):
        if not (statement.claimant_expert and statement.respondent_expert):
            raise StatementLockedError(
                "Both experts must sign before locking"
            )

        return statement.__class__(
            **{**statement.__dict__, "locked": True}
        )
