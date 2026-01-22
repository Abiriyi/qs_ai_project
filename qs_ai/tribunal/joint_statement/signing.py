# qs_ai/tribunal/joint_statement/signing.py
import hashlib
from datetime import datetime
from qs_ai.tribunal.joint_statement.models import ExpertSignature


class ExpertSigner:

    def sign(self, expert_name, firm, role, payload):
        fingerprint = hashlib.sha256(
            repr(payload).encode("utf-8")
        ).hexdigest()

        return ExpertSignature(
            expert_name=expert_name,
            firm=firm,
            role=role,
            signed_at=datetime.utcnow(),
            digital_fingerprint=fingerprint,
        )
