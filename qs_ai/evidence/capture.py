from uuid import uuid4
from datetime import datetime
from qs_ai.evidence.models import EvidenceArtifact
from qs_ai.version import get_release_identity
from qs_ai.system.fingerprint import dependency_fingerprint

def capture_evidence(
    category: str,
    source: str,
    description: str,
    payload: dict,
    created_by: str = "system",
) -> EvidenceArtifact:
    return EvidenceArtifact(
        evidence_id=str(uuid4()),
        category=category,
        source=source,
        description=description,
        payload=payload,
        created_by=created_by,
        created_at=datetime.utcnow(),
    )

