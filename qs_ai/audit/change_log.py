"""
QS Audit Change Log

Provides an immutable, append-only audit trail for:
- Automated quantities
- QS overrides
- Approval decisions
- Rejections and revocations

This module is legally defensible and QS-grade.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


# -----------------------------
# Audit Record
# -----------------------------

@dataclass(frozen=True)
class AuditRecord:
    """
    Immutable audit event.
    """
    audit_id: str
    timestamp: datetime
    actor: str                # QS username / system / reviewer
    action: str               # e.g. AUTO_COMPUTE, OVERRIDE, APPROVE
    item_code: str
    previous_value: Any
    new_value: Any
    justification: str
    confidence_before: Optional[float] = None
    confidence_after: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# -----------------------------
# Audit Log Store
# -----------------------------

class AuditLog:
    """
    Append-only audit log.

    This object should be instantiated per BoQ session.
    """

    def __init__(self):
        self._records: List[AuditRecord] = []

    # -------------------------
    # Core append method
    # -------------------------

    def append(
        self,
        *,
        actor: str,
        action: str,
        item_code: str,
        previous_value: Any,
        new_value: Any,
        justification: str,
        confidence_before: Optional[float] = None,
        confidence_after: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditRecord:
        """
        Append a new audit record.
        """

        record = AuditRecord(
            audit_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            actor=actor,
            action=action,
            item_code=item_code,
            previous_value=previous_value,
            new_value=new_value,
            justification=justification,
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            metadata=metadata or {},
        )

        self._records.append(record)
        return record

    # -------------------------
    # Read-only access
    # -------------------------

    def all(self) -> List[AuditRecord]:
        """
        Return all audit records (read-only).
        """
        return list(self._records)

    def filter_by_item(self, item_code: str) -> List[AuditRecord]:
        """
        Get audit history for a specific BoQ item.
        """
        return [r for r in self._records if r.item_code == item_code]

    def filter_by_action(self, action: str) -> List[AuditRecord]:
        """
        Filter audit events by action type.
        """
        return [r for r in self._records if r.action == action]

    # -------------------------
    # Export helpers
    # -------------------------

    def to_dicts(self) -> List[Dict[str, Any]]:
        """
        Serialize audit log for persistence / export.
        """
        return [
            {
                "audit_id": r.audit_id,
                "timestamp": r.timestamp.isoformat(),
                "actor": r.actor,
                "action": r.action,
                "item_code": r.item_code,
                "previous_value": r.previous_value,
                "new_value": r.new_value,
                "justification": r.justification,
                "confidence_before": r.confidence_before,
                "confidence_after": r.confidence_after,
                "metadata": r.metadata,
            }
            for r in self._records
        ]

    def __len__(self):
        return len(self._records)
