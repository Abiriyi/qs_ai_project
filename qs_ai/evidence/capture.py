from uuid import uuid4
from datetime import datetime
from typing import Dict, Any, Optional

from qs_ai.evidence.models import EvidenceRef
from qs_ai.evidence.hasher import hash_payload


def capture_evidence(
    *,
    category: str,
    source: str,
    description: str,
    payload: Dict[str, Any],
    created_by: Optional[str] = None,
) -> EvidenceRef:
    content_hash = hash_payload(payload)

    return EvidenceRef(
        evidence_id=str(uuid4()),
        category=category,
        source=source,
        description=description,
        payload=payload,
        content_hash=content_hash,
        created_at=datetime.utcnow(),
        created_by=created_by,
    )
