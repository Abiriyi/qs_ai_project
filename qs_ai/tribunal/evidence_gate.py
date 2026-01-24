from qs_ai.tribunal.evidence_crossref import EvidenceCrossReferenceEngine
from typing import List, Dict

class EvidenceSufficiencyGate:

    def __init__(self, crossref_engine):
        self.crossref = crossref_engine

    def check(self, artefact_id, required_categories):
        refs = self.crossref.get_evidence_for(artefact_id)

        present_categories = {r["category"] for r in refs}
        missing = [
            c for c in required_categories
            if c not in present_categories
        ]

        return {
            "artefact_id": artefact_id,
            "sufficient": len(missing) == 0,
            "missing": missing,
            "warnings": []
        }



