from uuid import uuid4
from datetime import datetime
from qs_ai.evidence.models import EvidenceArtifact
from qs_ai.version import get_release_identity
from qs_ai.system.fingerprint import dependency_fingerprint
from qs_ai.evidence.models import EvidenceRecord
from qs_ai.evidence.store import EvidenceStore

_STORE = EvidenceStore()

def capture_evidence(
    category,
    source,
    description,
    payload,
    created_by="system",
):
    previous = _STORE.all()[-1] if _STORE.all() else None
    prev_hash = previous.record_hash if previous else None

    base = {
        "category": category,
        "source": source,
        "description": description,
        "payload": payload,
        "created_by": created_by,
        "dependency_fingerprint": dependency_fingerprint(),
        "previous_hash": prev_hash,
    }

    record_hash = EvidenceRecord.compute_hash(base)

    record = EvidenceRecord(
        evidence_id=str(uuid4()),
        created_at=datetime.utcnow(),
        record_hash=record_hash,
        **base,
    )

    _STORE.append(record)
    return record

