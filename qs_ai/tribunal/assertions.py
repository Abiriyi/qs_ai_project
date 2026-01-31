from qs_ai.evidence.verify import verify_chain

def assert_evidence_integrity(evidence_records):
    ok, broken_id = verify_chain(evidence_records)
    if not ok:
        raise ValueError(
            f"Evidence tampering detected at record {broken_id}"
        )
    