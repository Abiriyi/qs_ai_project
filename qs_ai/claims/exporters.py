# qs_ai/claims/exporters.py
import json
from dataclasses import asdict
from qs_ai.claims.models import ClaimPackage


class ClaimExporter:

    @staticmethod
    def to_json(claim: ClaimPackage) -> str:
        return json.dumps(asdict(claim), indent=2, default=str)

    @staticmethod
    def to_dict(claim: ClaimPackage) -> dict:
        return asdict(claim)
