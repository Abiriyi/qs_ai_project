from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import json

@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    category: str
    source: str
    description: str
    payload: Dict
    created_at: datetime
    created_by: str
    dependency_fingerprint: str
    previous_hash: Optional[str]
    record_hash: str

    @staticmethod
    def compute_hash(data: Dict) -> str:
        blob = json.dumps(data, sort_keys=True, default=str).encode()
        return hashlib.sha256(blob).hexdigest()
