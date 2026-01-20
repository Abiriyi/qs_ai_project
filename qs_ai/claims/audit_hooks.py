# qs_ai/claims/audit_hooks.py
from datetime import datetime
from typing import Dict, Any


class ClaimAuditLogger:

    def log_creation(self, claim_id: str, user: str) -> Dict[str, Any]:
        return {
            "claim_id": claim_id,
            "action": "CREATED",
            "timestamp": datetime.utcnow().isoformat(),
            "user": user,
        }

    def log_approval(self, claim_id: str, approver: str) -> Dict[str, Any]:
        return {
            "claim_id": claim_id,
            "action": "APPROVED",
            "timestamp": datetime.utcnow().isoformat(),
            "user": approver,
        }

    def log_revision(self, claim_id: str, user: str, reason: str) -> Dict[str, Any]:
        return {
            "claim_id": claim_id,
            "action": "REVISED",
            "timestamp": datetime.utcnow().isoformat(),
            "user": user,
            "reason": reason,
        }
