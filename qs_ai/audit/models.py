from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
import json
import hashlib


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    event_type: str
    actor_id: str
    artefact_type: str
    artefact_id: str
    timestamp: datetime
    evidence_refs: List[str]
    details: dict
    previous_hash: Optional[str]
    event_hash: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str, sort_keys=True)

    @staticmethod
    def compute_hash(payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
