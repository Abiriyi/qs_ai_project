class EvidenceCrossReferenceEngine:
    def __init__(self):
        self.references = []

    def link(self, artefact_id: str, evidence, relevance="primary"):
        self.references.append({
            "artefact_id": artefact_id,
            "evidence_id": evidence.evidence_id,
            "category": evidence.category,
            "description": evidence.description,
            "relevance": relevance,
        })

    def get_evidence_for(self, artefact_id: str):
        return [
            r for r in self.references
            if r["artefact_id"] == artefact_id
        ]
