"""
QS Approval Workflow Engine

Implements a strict finite state machine (FSM) for:
- QS overrides
- Senior QS approval
- Rejection and revocation

This module enforces professional QS governance.
"""

from enum import Enum
from typing import Optional

from qs_ai.audit.change_log import AuditLog
from qs_ai.qs_override.models import QSOverrideRecord
from qs_ai.qs_override.exceptions import (
    InvalidApprovalTransition,
    UnauthorizedAction,
)


# -----------------------------
# Approval States
# -----------------------------

class ApprovalState(str, Enum):
    DRAFT = "DRAFT"                     # QS preparing override
    SUBMITTED = "SUBMITTED"             # Submitted for review
    APPROVED = "APPROVED"               # Senior QS approved
    REJECTED = "REJECTED"               # Rejected by reviewer
    REVOKED = "REVOKED"                 # Withdrawn after approval


# -----------------------------
# Approval Engine
# -----------------------------

class ApprovalEngine:
    """
    Finite state machine enforcing QS approval rules.
    """

    def __init__(self, audit_log: AuditLog):
        self.audit_log = audit_log

    # -------------------------
    # State transitions
    # -------------------------

    def submit(self, override: QSOverrideRecord, actor: str):
        self._assert_state(override, ApprovalState.DRAFT)
        override.state = ApprovalState.SUBMITTED

        self._audit(
            actor=actor,
            action="SUBMIT_OVERRIDE",
            override=override,
            justification="Override submitted for senior QS review",
        )

    def approve(self, override: QSOverrideRecord, actor: str, senior: bool = False):
        if not senior:
            raise UnauthorizedAction("Only Senior QS may approve overrides")

        self._assert_state(override, ApprovalState.SUBMITTED)
        override.state = ApprovalState.APPROVED

        self._audit(
            actor=actor,
            action="APPROVE_OVERRIDE",
            override=override,
            justification="Override approved by Senior QS",
        )

    def reject(self, override: QSOverrideRecord, actor: str, reason: str, senior: bool = False):
        if not senior:
            raise UnauthorizedAction("Only Senior QS may reject overrides")

        self._assert_state(override, ApprovalState.SUBMITTED)
        override.state = ApprovalState.REJECTED

        self._audit(
            actor=actor,
            action="REJECT_OVERRIDE",
            override=override,
            justification=reason,
        )

    def revoke(self, override: QSOverrideRecord, actor: str):
        self._assert_state(override, ApprovalState.APPROVED)
        override.state = ApprovalState.REVOKED

        self._audit(
            actor=actor,
            action="REVOKE_OVERRIDE",
            override=override,
            justification="Override revoked after approval",
        )

    # -------------------------
    # Guards
    # -------------------------

    def _assert_state(self, override: QSOverrideRecord, expected: ApprovalState):
        if override.state != expected:
            raise InvalidApprovalTransition(
                f"Invalid transition: {override.state} → expected {expected}"
            )

    # -------------------------
    # Audit helper
    # -------------------------

    def _audit(self, *, actor: str, action: str, override: QSOverrideRecord, justification: str):
        self.audit_log.append(
            actor=actor,
            action=action,
            item_code=override.item_code,
            previous_value=override.original_quantity,
            new_value=override.override_quantity,
            justification=justification,
            confidence_before=override.original_confidence,
            confidence_after=override.override_confidence,
            metadata={
                "override_id": override.override_id,
                "state": override.state,
            },
        )
