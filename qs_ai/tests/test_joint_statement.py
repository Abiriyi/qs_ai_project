# qs_ai/tests/test_joint_statement.py
import pytest
from qs_ai.tribunal.joint_statement.workflow import JointStatementWorkflow
from qs_ai.tribunal.joint_statement.exceptions import StatementLockedError


def test_joint_statement_lock_requires_both_signatures(mock_statement, mock_signature):
    wf = JointStatementWorkflow()

    with pytest.raises(StatementLockedError):
        wf.lock(mock_statement)
