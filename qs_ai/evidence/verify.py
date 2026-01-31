def verify_chain(records):
    previous = None
    for r in records:
        base = {
            "category": r.category,
            "source": r.source,
            "description": r.description,
            "payload": r.payload,
            "created_by": r.created_by,
            "dependency_fingerprint": r.dependency_fingerprint,
            "previous_hash": previous.record_hash if previous else None,
        }
        expected = r.compute_hash(base)
        if expected != r.record_hash:
            return False, r.evidence_id
        previous = r
    return True, None
