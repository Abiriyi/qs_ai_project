import hashlib
import json
from qs_ai.approval.exceptions import ApprovalError


def seal_artefact(data: dict) -> str:
    """
    Generates an immutable hash of approved data
    """
    serialised = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialised.encode()).hexdigest()


def assert_not_modified(original_hash: str, current_data: dict):
    current_hash = seal_artefact(current_data)
    if current_hash != original_hash:
        raise ApprovalError("Approved artefact has been modified")
